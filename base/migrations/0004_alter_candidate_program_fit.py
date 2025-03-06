# Generated by Django 5.1.6 on 2025-03-06 06:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0003_rename_scores_candidate_gpa"),
    ]

    operations = [
        migrations.AlterField(
            model_name="candidate",
            name="program_fit",
            field=models.CharField(
                choices=[
                    ("civil_engineering", "Civil Engineering"),
                    ("mechanical_engineering", "Mechanical Engineering"),
                    ("electrical_engineering", "Electrical Engineering"),
                    ("computer_engineering", "Computer Engineering"),
                    ("chemical_engineering", "Chemical Engineering"),
                    ("biomedical_engineering", "Biomedical Engineering"),
                    ("aerospace_engineering", "Aerospace Engineering"),
                    ("industrial_engineering", "Industrial Engineering"),
                    ("software_engineering", "Software Engineering"),
                    ("math", "Math"),
                    ("science", "Science"),
                    ("business", "Business"),
                    ("arts", "Arts"),
                ],
                default="engineering",
                max_length=50,
            ),
        ),
    ]
