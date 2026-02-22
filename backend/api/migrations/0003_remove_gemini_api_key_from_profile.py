# Generated manually - remove user API key; app uses server config only

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_userprofile_avatar_url'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='gemini_api_key',
        ),
    ]
