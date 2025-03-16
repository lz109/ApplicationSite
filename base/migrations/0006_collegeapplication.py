# Generated by Django 5.1.6 on 2025-03-14 03:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0005_candidate_academic_experience_candidate_projects_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="CollegeApplication",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("college_name", models.CharField(max_length=255)),
                (
                    "application_status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("accepted", "Accepted"),
                            ("rejected", "Rejected"),
                            ("waitlisted", "Waitlisted"),
                        ],
                        default="pending",
                        max_length=50,
                    ),
                ),
                (
                    "candidate",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="applications",
                        to="base.candidate",
                    ),
                ),
            ],
        ),
    ]
