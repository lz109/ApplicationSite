# Generated by Django 4.2.20 on 2025-05-08 17:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0013_alter_candidate_application_status_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="profile_photo",
            field=models.ImageField(blank=True, null=True, upload_to="profile_photos/"),
        ),
    ]
