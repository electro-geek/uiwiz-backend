from rest_framework import serializers
from django.contrib.auth.models import User
from .models import ChatSession, ChatMessage, CodeVersion, UserProfile
from .utils import encrypt_data, decrypt_data

class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    email = serializers.ReadOnlyField(source='user.email')
    
    class Meta:
        model = UserProfile
        fields = ('gemini_api_key', 'username', 'email', 'avatar_url')

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        # Decrypt API key before returning it in API responses
        # Handles legacy plain text automatically via decrypt_data
        if ret.get('gemini_api_key'):
            ret['gemini_api_key'] = decrypt_data(ret['gemini_api_key'])
        return ret

    def create(self, validated_data):
        # Encrypt API key before saving
        if 'gemini_api_key' in validated_data and validated_data['gemini_api_key']:
            validated_data['gemini_api_key'] = encrypt_data(validated_data['gemini_api_key'])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Encrypt API key before saving
        if 'gemini_api_key' in validated_data and validated_data['gemini_api_key']:
            validated_data['gemini_api_key'] = encrypt_data(validated_data['gemini_api_key'])
        return super().update(instance, validated_data)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class CodeVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodeVersion
        fields = '__all__'

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = '__all__'

class ChatSessionSerializer(serializers.ModelSerializer):
    messages = ChatMessageSerializer(many=True, read_only=True)
    versions = CodeVersionSerializer(many=True, read_only=True)

    class Meta:
        model = ChatSession
        fields = ('id', 'title', 'created_at', 'updated_at', 'messages', 'versions')
