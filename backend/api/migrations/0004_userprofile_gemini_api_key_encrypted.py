# Generated for per-user Gemini API key (stored encrypted)

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_remove_gemini_api_key_from_profile'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='gemini_api_key_encrypted',
            field=models.TextField(blank=True, null=True),
        ),
    ]
