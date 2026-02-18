"""
API Views for UIWiz - AI-Powered UI Generator.
Handles code generation via Gemini API with streaming support and automatic failover.
"""
import json
import re

from django.conf import settings
from django.http import StreamingHttpResponse, JsonResponse
from django.contrib.auth.models import User
from rest_framework import status, permissions, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes

import google.generativeai as genai
from google.api_core.exceptions import (
    ResourceExhausted, ServiceUnavailable, InternalServerError,
    InvalidArgument, PermissionDenied, Unauthenticated
)
from .models import ChatSession, ChatMessage, CodeVersion, UserProfile
from .serializers import (
    UserSerializer, ChatSessionSerializer, 
    ChatMessageSerializer, CodeVersionSerializer,
    UserProfileSerializer
)

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserSerializer

class SessionListView(generics.ListCreateAPIView):
    serializer_class = ChatSessionSerializer
    
    def get_queryset(self):
        return ChatSession.objects.filter(user=self.request.user).order_by('-updated_at')
        
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class SessionDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = ChatSessionSerializer
    
    def get_queryset(self):
        return ChatSession.objects.filter(user=self.request.user)

class UserProfileView(APIView):
    def get(self, request):
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)

    def post(self, request):
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        profile.gemini_api_key = None
        profile.save()
        return Response({'status': 'API key deleted'})


# Fallback models to try if the primary model hits a rate limit
# Ordered by preference/similarity to latest flash models
FALLBACK_MODELS = [
    'gemini-2.0-flash',
    'gemini-2.0-flash-lite',
    'gemini-flash-latest',
    'gemini-pro-latest',
    'gemini-3-flash-preview',
    'gemini-2.5-flash-preview-09-2025',
]

# System instruction for Gemini
SYSTEM_INSTRUCTION = """You are a world-class Frontend Engineer and UI/UX Designer. 
Your goal is to output **strictly** executable React code using Tailwind CSS that represents a **full, production-ready web application**.

1. **Complete Application**: Don't just build a component; build a complete page or mini-app with a consistent theme. Include headers, footers, sidebars, and main content areas where appropriate.
2. **Strict Output**: Only return the code; no markdown backticks, no explanations. No "Here is the code...". Just start with imports.
3. **Architecture**: Generate a production-ready, multi-file project structure (React + Vite). 
4. **Multi-file Output**: Output **ONLY** a strictly valid JSON object. Do not wrap it in markdown backticks in your raw output (though the UI might handle them). 
   - Keys MUST be file paths starting with `/` (e.g., `/App.tsx`, `/components/Header.tsx`).
   - Values MUST be raw string content of the files.
   - **CRITICAL**: Do not use markdown code blocks (```) inside the JSON values.
   - You **MUST** include a `/App.tsx` which imports and uses the other components.
5. **No Conversational Text**: Do not include any text before or after the JSON. No "Sure, here is your app...". Just the JSON.
6. **Visual Excellence**:
   - Use `lucide-react` for all icons.
   - Use `framer-motion` for sophisticated animations and transitions.
   - Use `clsx` and `tailwind-merge` for class management (cn utility).
   - Use `recharts` for any data visualization.
   - Use `react-router-dom` for multi-page apps.
   - Use `lucide-react`, `framer-motion`, `clsx`, `tailwind-merge`, `recharts`, `date-fns`, `react-router-dom`, `re-resizable`, `axios`.
7. **Replication**: If the user provides an image, replicate it perfectly using this multi-file structure.
8. **Mobile First**: All components must be fully responsive using Tailwind (`sm:`, `md:`, `lg:`).
9. **Modern Stack**: Assume a standard Vite + React + Tailwind + TypeScript environment.
"""


def clean_code_response(text: str) -> str:
    """Extract code/JSON from potential conversational text or markdown blocks."""
    cleaned = text.strip()
    
    # Try to find a markdown block (json or generic)
    match = re.search(r'```(?:json|jsx|javascript|tsx|ts|typescript|js|react)?\s*\n?(.*?)(?:```|$)', cleaned, re.DOTALL | re.IGNORECASE)
    if match:
        content = match.group(1).strip()
        # If it's valid JSON, return it
        try:
            json.loads(content)
            return content
        except:
            pass
        return content
    
    # If no markdown block, check if the whole text is JSON
    try:
        json.loads(cleaned)
        return cleaned
    except:
        pass
        
    return cleaned


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def root_view(request):
    return Response({
        'message': 'UIWiz API is running',
        'health_check': '/api/health/',
        'version': '1.0.0'
    })

class HealthCheckView(APIView):
    """Health check endpoint."""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        gemini_configured = False
        if request.user.is_authenticated:
            try:
                gemini_configured = bool(request.user.profile.gemini_api_key)
            except UserProfile.DoesNotExist:
                gemini_configured = False
        else:
            # For anonymous health check, just return backend status
            gemini_configured = False

        return Response({
            'status': 'healthy',
            'service': 'UIWiz Backend',
            'gemini_configured': gemini_configured,
        })


def generate_chat_title(api_key, first_prompt):
    """Generate a concise, 3-5 word title for the chat using Gemini."""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Use a more structured prompt to avoid issues with special characters in user input
        ai_prompt = (
            "You are a helpful assistant. Your task is to generate a very short, concise, and catchy "
            "title for a new web development project based on the user's initial prompt.\n\n"
            "User's request: \"\"\"" + first_prompt[:1000] + "\"\"\"\n\n"
            "Generate a title (max 4-5 words). Do not use any quotes, backticks, or special characters. "
            "Just return the title text itself."
        )
        
        response = model.generate_content(ai_prompt)
        title = response.text.strip()
        
        # Thorough cleaning of the generated title
        title = re.sub(r'["\'`*_#]', '', title)
        title = title.split('\n')[0].strip() # Take only the first line
        
        if not title or len(title) < 2:
            return first_prompt[:50] + ('...' if len(first_prompt) > 50 else '')
            
        return title[:100]
    except Exception as e:
        print(f"Error generating chat title: {str(e)}")
        return first_prompt[:50] + ('...' if len(first_prompt) > 50 else '')


class GenerateCodeView(APIView):
    """
    Generate React component code using Gemini API.
    Supports:
    - Text prompts
    - Image uploads (base64)
    - Iterative refinement (previous code context)
    - Streaming responses via SSE
    - Automatic failover/retry on rate limits (429)
    - AI-generated session titles
    """

    def post(self, request):
        prompt = request.data.get('prompt', '')
        image_data = request.data.get('image', None)
        previous_code = request.data.get('previousCode', None)
        use_streaming = request.data.get('stream', True)
        session_id = request.data.get('sessionId', None)

        if not prompt:
            return Response(
                {'error': 'Prompt is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not session_id:
            return Response(
                {'error': 'Session ID is required for persistence'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            session = ChatSession.objects.get(id=session_id, user=request.user)
        except ChatSession.DoesNotExist:
            return Response(
                {'error': 'Invalid session ID'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Save user message
        ChatMessage.objects.create(session=session, role='user', content=prompt)
        
        # Get API key from user profile
        try:
            profile = request.user.profile
            api_key = profile.gemini_api_key
        except UserProfile.DoesNotExist:
            api_key = None

        if not api_key:
            return Response(
                {'error': 'Gemini API key not found. Please provide your own API key in settings.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # update session title if it's new
        if session.title == 'New Chat':
            session.title = generate_chat_title(api_key, prompt)
            session.save()

        # Configure Gemini
        genai.configure(api_key=api_key)

        # Prepare parts
        parts = []
        if previous_code:
            parts.append(
                f"Here is the current code that needs to be refined:\n\n{previous_code}\n\n"
                f"User's refinement request: {prompt}"
            )
        else:
            parts.append(prompt)

        if image_data:
            import base64
            if ',' in image_data:
                image_data = image_data.split(',')[1]
            image_bytes = base64.b64decode(image_data)
            parts.append({
                'mime_type': 'image/png',
                'data': image_bytes
            })

        # Prepare list of models to try
        primary_model = settings.GEMINI_MODEL
        models_to_try = [primary_model] + [
            m for m in FALLBACK_MODELS 
            if m != primary_model
        ]

        if use_streaming:
            return self._stream_with_retry(models_to_try, parts, session, prompt)
        else:
            return self._blocking_with_retry(models_to_try, parts, session, prompt)

    def _blocking_with_retry(self, models, parts, session, prompt):
        """Try models sequentially until one succeeds or all fail."""
        last_error = None

        for model_name in models:
            try:
                print(f"Attempting generation with model: {model_name}")
                model = genai.GenerativeModel(
                    model_name=model_name,
                    system_instruction=SYSTEM_INSTRUCTION,
                )
                response = model.generate_content(parts)
                code = clean_code_response(response.text)
                
                # Save assistant response
                ChatMessage.objects.create(session=session, role='assistant', content="I've generated the component.")
                CodeVersion.objects.create(session=session, prompt=prompt, code=code)
                
                return Response({'code': code})

            except (ResourceExhausted, ServiceUnavailable, InternalServerError) as e:
                print(f"Model {model_name} failed with error: {e}")
                last_error = e
                continue
            except (InvalidArgument, PermissionDenied, Unauthenticated) as e:
                return Response(
                    {'error': 'Your Gemini API key is invalid or has expired. Please create a new one in settings.'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            except Exception as e:
                # Non-retriable error
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        return Response(
            {'error': f"All models failed. Last error: {last_error}"},
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )

    def _stream_with_retry(self, models, parts, session, prompt):
        """Stream response with robust retry logic inside the generator."""
        
        def event_stream():
            success = False
            last_error = None
            accumulated_code = ""

            for model_name in models:
                try:
                    yield f": attempting {model_name}\n\n"

                    model = genai.GenerativeModel(
                        model_name=model_name,
                        system_instruction=SYSTEM_INSTRUCTION,
                    )
                    
                    response = model.generate_content(parts, stream=True)
                    
                    for chunk in response:
                        if chunk.text:
                            accumulated_code += chunk.text
                            data = json.dumps({'type': 'chunk', 'content': chunk.text})
                            yield f"data: {data}\n\n"
                    
                    # Persist on success
                    ChatMessage.objects.create(session=session, role='assistant', content="I've generated the component.")
                    CodeVersion.objects.create(session=session, prompt=prompt, code=clean_code_response(accumulated_code))
                    
                    yield f"data: {json.dumps({'type': 'done'})}\n\n"
                    success = True
                    break

                except (ResourceExhausted, ServiceUnavailable, InternalServerError) as e:
                    print(f"Streaming failed for {model_name}: {e}")
                    last_error = e
                    continue
                except (InvalidArgument, PermissionDenied, Unauthenticated) as e:
                    print(f"Auth error for {model_name}: {e}")
                    error_data = json.dumps({
                        'type': 'error', 
                        'content': 'Your Gemini API key is invalid or has expired. Please create a new one in settings.'
                    })
                    yield f"data: {error_data}\n\n"
                    return
                except Exception as e:
                    print(f"Non-retriable error for {model_name}: {e}")
                    error_data = json.dumps({'type': 'error', 'content': str(e)})
                    yield f"data: {error_data}\n\n"
                    return

            if not success:
                error_msg = f"All models failed. Last error: {last_error}"
                error_data = json.dumps({'type': 'error', 'content': error_msg})
                yield f"data: {error_data}\n\n"

        response = StreamingHttpResponse(
            event_stream(),
            content_type='text/event-stream'
        )
        response['Cache-Control'] = 'no-cache'
        response['X-Accel-Buffering'] = 'no'
        return response
