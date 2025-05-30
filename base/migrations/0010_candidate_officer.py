# Generated by Django 5.1.6 on 2025-03-16 19:52

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0009_remove_message_receiver_message_receiver_email"),
    ]

    operations = [
        migrations.AddField(
            model_name="candidate",
            name="officer",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="candidates",
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=False,
        ),
    ]
