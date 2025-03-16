from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils.timezone import now

class User(AbstractUser):
    ROLE_CHOICES = [
        ("admin", "Admin"),
        ("officer", "Admission Officer"),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="officer")
    job_title = models.CharField(max_length=255, blank=True, null=True)
    class Meta:
        app_label = "base"

    groups = models.ManyToManyField(
        Group,
        related_name="base_user_groups",  
        blank=True,
        help_text="The groups this user belongs to.",
        verbose_name="groups",
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name="base_user_permissions",  
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions",
    )

# Candidate Model
class Candidate(models.Model):
    PROGRAM_CHOICES = (
    ('civil_engineering', 'Civil Engineering'),
    ('mechanical_engineering', 'Mechanical Engineering'),
    ('electrical_engineering', 'Electrical Engineering'),
    ('computer_engineering', 'Computer Engineering'),
    ('chemical_engineering', 'Chemical Engineering'),
    ('biomedical_engineering', 'Biomedical Engineering'),
    ('aerospace_engineering', 'Aerospace Engineering'),
    ('industrial_engineering', 'Industrial Engineering'),
    ('software_engineering', 'Software Engineering'),
    ('math', 'Math'),
    ('science', 'Science'),
    ('business', 'Business'),
    ('arts', 'Arts'),
)

    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('waitlisted', 'Waitlisted'),
    )
    
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    program_fit = models.CharField(max_length=50, choices=PROGRAM_CHOICES, default='engineering')
    gpa = models.FloatField(default=0.0)
    application_status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="pending")
    shortlisted = models.BooleanField(default=False)

    academic_experience = models.TextField(blank=True, null=True)  # Education & coursework
    skills = models.TextField(blank=True, null=True)  # List of technical & soft skills
    projects = models.TextField(blank=True, null=True)

    officer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="candidates")
    def __str__(self):
        return self.name


class CollegeApplication(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('waitlisted', 'Waitlisted'),
    )

    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name="applications")
    college_name = models.CharField(max_length=255)
    application_status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="pending")

    def __str__(self):
        return f"{self.candidate.name} - {self.college_name} ({self.application_status})"

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver_email = models.EmailField()
    content = models.TextField()
    timestamp = models.DateTimeField(default=now)

# Event Model
class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateTimeField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    members = models.ManyToManyField(Candidate, blank=True)  

    def __str__(self):
        return self.title


class ActivityLog(models.Model):
    officer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="actions")
    action = models.CharField(max_length=255)  # Example: "accepted candidate"
    candidate = models.ForeignKey("Candidate", on_delete=models.CASCADE, null=True, blank=True)
    timestamp = models.DateTimeField(default=now)

    def __str__(self):
        return f'{self.officer.username} {self.action} candidate {self.candidate.name} at {self.timestamp}'

