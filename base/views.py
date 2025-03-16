from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .forms import RegisterForm, SignInForm
from .models import User
from .models import Candidate, Message, Event, ActivityLog, CollegeApplication
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import UserProfileForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q, F
from django.utils.timezone import now

from .forms import EditProfileForm
from .forms import AddOfficerForm
import logging

import pymupdf as fitz  # PyMuPDF
import os
import docx
import pytesseract
from pdf2image import convert_from_path
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from .forms import DocumentUploadForm
from PIL import Image
import re
from django.db.models.functions import Lower
from django.db import IntegrityError


def home(request): 
    return render(request, "home.html")

def signup(request):
    # if request.user.is_authenticated:
    #     return redirect("/dashboard")
    
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect("/dashboard")
        else:
            messages.error(request, "Registration failed.")
    
    else:
        form = RegisterForm()
    
    return render(request, "signup.html", {"form": form})

def signin(request):
    if request.user.is_authenticated:
        return redirect("/dashboard")
    
    if request.method == "POST":
        form = SignInForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Login successful.")
                return redirect("/dashboard")
            else:
                messages.error(request, "Invalid credentials.")
    
    else:
        form = SignInForm()
    
    return render(request, "signin.html", {"form": form})

def signout(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect("/")

def is_admin(user):
    return user.role == "admin"

def is_officer(user):
    return user.role == "officer"

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    return render(request, "admin_dashboard.html")

def normalize_text(text):
    """Normalize text by removing spaces, underscores, and converting to lowercase."""
    return re.sub(r'[\s_]+', '', text).lower()

@login_required
@user_passes_test(is_officer)
def officer_dashboard(request):
    program_fit_filter = request.GET.get("program_fit", "")
    application_status_filter = request.GET.get("application_status", "")
    college_filter = request.GET.get("college_name", "")
    score_sort = request.GET.get("score_sort", "")

    candidates = Candidate.objects.all()
    events = Event.objects.all().order_by("-date")

    if program_fit_filter:
        normalized_filter = normalize_text(program_fit_filter)
        candidates = candidates.filter(program_fit__iexact=normalized_filter)

    if application_status_filter:
        candidates = candidates.filter(applications__application_status=application_status_filter)
    if college_filter:
        candidates = candidates.filter(applications__college_name__icontains=college_filter).distinct()
    if score_sort == "high_to_low":
        candidates = candidates.order_by(F("gpa").desc())
    elif score_sort == "low_to_high":
        candidates = candidates.order_by(F("gpa").asc())

    # Handle file upload
    extracted_data = None
    form = DocumentUploadForm()

    if request.method == "POST":
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = form.cleaned_data['file']
            fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'uploads'))
            filename = fs.save(uploaded_file.name, uploaded_file)
            file_path = fs.path(filename)

            if uploaded_file.name.endswith(".pdf"):
                extracted_text = extract_text_from_pdf(file_path)
            elif uploaded_file.name.endswith(".docx"):
                extracted_text = extract_text_from_docx(file_path)
            else:
                messages.error(request, "Unsupported file format. Only PDF and DOCX are allowed.")
                return redirect("officer_dashboard")

            extracted_data = process_extracted_text(extracted_text)

            # Convert GPA to float safely
            gpa_value = None
            try:
                gpa_value = float(extracted_data["gpa"])
            except ValueError:
                gpa_value = None

            try:
                # Ensure candidate is saved in DB
                candidate, created = Candidate.objects.update_or_create(
                    name = extracted_data["name"].replace("Name: ", ""),
                     
                    defaults={
                        "email": extracted_data["email"], 
                        "gpa": gpa_value,
                        "program_fit": extracted_data["program"],
                        "application_status": "pending"
                    }
                )

                if created:
                    messages.success(request, "Candidate details extracted and saved successfully!")
                else:
                    messages.info(request, "Candidate already exists. Updated existing entry.")

            except IntegrityError as e:
                print("Database error:", e)
                messages.error(request, "Error saving candidate data. Please check for duplicates.")

            candidates = Candidate.objects.all()

    return render(request, "officer_dashboard.html", {
        "candidates": candidates,
        "events": events,
        "form": form,
        "extracted_data": extracted_data
    })


@login_required
@user_passes_test(is_officer)
def update_candidate_status(request, candidate_id):
    application = get_object_or_404(CollegeApplication, id=candidate_id)

    if request.method == "POST":
        new_status = request.POST.get("application_status")  # Get new status from form

        if new_status in ["pending", "accepted", "rejected", "waitlisted"]:
            old_status = application.application_status
            application.application_status = new_status
            application.save()

            # Log the officer's action
            ActivityLog.objects.create(
                officer=request.user,
                action=f"changed {application.college_name} status from {old_status} to {new_status}",
                candidate=application.candidate
            )

            messages.success(request, f"Application status for {application.college_name} updated to {new_status}.")
        else:
            messages.error(request, "Invalid status selected.")

    return redirect("officer_dashboard")


@login_required
def send_message(request):
    if request.method == "POST":
        candidate_id = request.POST.get("candidate_id")
        candidate = get_object_or_404(Candidate, id=candidate_id)
        content = request.POST.get("content")
        if content:
            Message.objects.create(sender=request.user, receiver_email=candidate.email, content=content, timestamp=now())
            messages.success(request, "Message sent successfully.")
    return redirect("officer_dashboard")

@login_required
def send_message_to_user(request):
    if request.method == "POST":
        recipient_email = request.POST.get("recipient_email").strip()
        content = request.POST.get("content").strip()

        if not content:
            messages.error(request, "Message content cannot be empty.")
            return redirect("messages_page")

        if not recipient_email:
            messages.error(request, "Please select a recipient.")
            return redirect("messages_page")

        # Ensure the recipient exists in the system
        recipient = User.objects.filter(email=recipient_email).first()
        if not recipient:
            messages.error(request, "Invalid recipient. User does not exist.")
            return redirect("messages_page")

        # Create and save the message
        Message.objects.create(sender=request.user, receiver_email=recipient_email, content=content)
        messages.success(request, f"Message sent to {recipient.username}.")

    return redirect("messages_page")

@login_required
def message_page(request):
    users = User.objects.exclude(id=request.user.id)  # Get all users except the logged-in user
    candidates = Candidate.objects.all()  # Get all candidates

    # Messages sent by the logged-in officer/admin
    messages_sent = Message.objects.filter(sender=request.user).order_by("-timestamp")

    # Messages received by the logged-in officer/admin
    messages_received = Message.objects.filter(receiver_email=request.user.email).order_by("-timestamp")

    # Separate messages between officers and between candidates
    officer_sent_messages = messages_sent.filter(receiver_email__in=users.values_list('email', flat=True))
    candidate_sent_messages = messages_sent.exclude(receiver_email__in=users.values_list('email', flat=True))

    officer_received_messages = messages_received.filter(sender__in=users)
    candidate_received_messages = messages_received.exclude(sender__in=users)

    return render(request, "messages.html", {
        "users": users,
        "candidates": candidates,
        "officer_sent_messages": officer_sent_messages,
        "candidate_sent_messages": candidate_sent_messages,
        "officer_received_messages": officer_received_messages,
        "candidate_received_messages": candidate_received_messages,
    })


@login_required
def dashboard(request):
    if request.user.role == "admin":
        return redirect("admin_dashboard")
    return redirect("officer_dashboard")

@login_required
@user_passes_test(is_officer)
def create_event(request):
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        date = request.POST.get("date")
        if title and description and date:
            Event.objects.create(title=title, description=description, date=date, created_by=request.user)
            messages.success(request, "Event created successfully.")
    return redirect("officer_dashboard")

@login_required
@user_passes_test(is_officer)
def invite_candidate_to_event(request):
    if request.method == "POST":
        event_id = request.POST.get("event_id")
        candidate_ids = request.POST.getlist("candidate_ids[]")  # Get multiple selected candidates

        event = get_object_or_404(Event, id=event_id)

        invited_candidates = []
        for candidate_id in candidate_ids:
            candidate = get_object_or_404(Candidate, id=candidate_id)
            event.members.add(candidate)  # Add candidate to event
            invited_candidates.append(candidate.name)

        if invited_candidates:
            messages.success(request, f"Invited {', '.join(invited_candidates)} to {event.title}.")
        else:
            messages.warning(request, "No candidates were selected.")

    return redirect("officer_dashboard")


@login_required
def view_profile(request):
    return render(request, "profile.html", {"user": request.user})


@login_required
def edit_profile(request):
    if request.method == "POST":
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("view_profile")  # Redirect back to the profile page
    else:
        form = EditProfileForm(instance=request.user)

    return render(request, "edit_profile.html", {"form": form})


# Ensure only admins can access this dashboard
def is_admin(user):
    return user.is_authenticated and user.role == "admin"

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    officers = User.objects.filter(role="officer")
    logs = ActivityLog.objects.all().order_by("-timestamp")[:20]  # Show the 20 most recent actions

    return render(request, "admin_dashboard.html", {"officers": officers, "logs": logs})


@login_required
@user_passes_test(is_admin)
def add_officer(request):
    if request.method == "POST":
        form = AddOfficerForm(request.POST)
        if form.is_valid():
            new_officer = form.save(commit=False)
            new_officer.role = "officer"
            new_officer.set_password(form.cleaned_data["password1"])
            new_officer.save()
            messages.success(request, "New officer account created successfully!")
            return redirect("admin_dashboard")
    else:
        form = AddOfficerForm()

    return render(request, "add_officer.html", {"form": form})

@login_required
@user_passes_test(is_admin)
def remove_officer(request, user_id):
    officer = get_object_or_404(User, id=user_id, role="officer")
    officer.delete()
    messages.success(request, "Officer account removed successfully!")
    return redirect("admin_dashboard")

logger = logging.getLogger(__name__)
logging.basicConfig(filename="logs/system.log", level=logging.INFO)

def log_event(message):
    logger.info(message)

def extract_text_from_scanned_pdf(file_path):
    images = convert_from_path(file_path)  # Convert PDF to images
    text = ""

    for image in images:
        text += pytesseract.image_to_string(image) + "\n"  # Apply OCR

    return text

def extract_text_from_pdf(file_path):
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()

    # If no text is extracted, apply OCR
    if not text.strip():
        text = extract_text_from_scanned_pdf(file_path)

    return text

import re
import re

def find_match(pattern, text):
    """Utility function to find a regex match or return 'Not Found'."""
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        try:
            return match.group(1).strip()
        except IndexError:
            print(f"IndexError: No group(1) found for pattern: {pattern} in text:\n{text}")
            return "Not Found"
    else:
        print(f"Pattern not found: {pattern} in text:\n{text}")
        return "Not Found"

def process_extracted_text(text):
    """ Extracts candidate information from resume text using regex. """
    name = find_match(r"Name[:\-\s]+([A-Z][a-zA-Z]+(?:\s[A-Z][a-zA-Z]+)*)\b(?!\s*Email)", text)

    # Extract Email (More flexible email regex)
    email = find_match(r"Email[:\-\s]*([\w\.-]+@[\w\.-]+\.\w+)", text)

    # Extract GPA (Handles GPA variations like "GPA: 3.8" or "GPA - 3.80")
    gpa = find_match(r"GPA[:\-\s]+(\d+\.\d+)", text)

    # Extract Program (Handles "Program Fit: Engineering" and similar)
    program = find_match(r"Program(?:\s*Fit)?[:\-\s]+([A-Za-z\s]+?)\b", text)

    # Extract Academic Experience, Skills, and Projects
    academic_experience = find_match(r"Academic Experience[:\-\s]+([\w\W]+?)(?:Skills|Projects|Colleges|Applied|Application Status|$)", text)
    skills = find_match(r"Skills[:\-\s]+([\w\W]+?)(?:Projects|Colleges|Applied|Application Status|$)", text)
    projects = find_match(r"Projects[:\-\s]+([\w\W]+?)(?:Colleges|Applied|Application Status|$)", text)

    # Extract Colleges Applied (fixes duplicate issues & captures comma-separated values correctly)
    colleges_applied = find_match(r"(?:Colleges Applied|Colleges|Applications)[:\-\s]+([A-Z][a-zA-Z\s]+(?:,\s*[A-Z][a-zA-Z\s]+)*)", text)

    return {
        "name": name,
        "email": email,
        "gpa": gpa,
        "program": program,
        "academic_experience": academic_experience,
        "skills": skills,
        "projects": projects,
        "colleges_applied": colleges_applied
    }

def extract_text_from_docx(file_path):
    text = ""
    doc = docx.Document(file_path)
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text



@login_required
@user_passes_test(is_officer)
def upload_document(request):
    extracted_text = None

    if request.method == "POST":
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = form.cleaned_data['file']
            fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'uploads'))
            filename = fs.save(uploaded_file.name, uploaded_file)
            file_path = fs.path(filename)

            # Extract text based on file type
            if uploaded_file.name.endswith(".pdf"):
                extracted_text = extract_text_from_pdf(file_path)
            elif uploaded_file.name.endswith(".docx"):
                extracted_text = extract_text_from_docx(file_path)
            else:
                messages.error(request, "Unsupported file format. Only PDF and DOCX are allowed.")
                return redirect("officer_dashboard")

            # Extract structured data
            extracted_data = process_extracted_text(extracted_text)

            gpa_value = None
            try:
                gpa_value = float(extracted_data["gpa"])
            except ValueError:
                gpa_value = None

            # Save to Candidate model
            candidate, created = Candidate.objects.get_or_create(
                email=extracted_data["email"],
                defaults={
                    "name": extracted_data["name"],
                    "gpa": gpa_value,
                    "program_fit": extracted_data["program"],
                    "academic_experience": extracted_data["academic_experience"],
                    "skills": extracted_data["skills"],
                    "projects": extracted_data["projects"]
                }
            )

            if created:
                messages.success(request, "Candidate details extracted and saved successfully!")
            else:
                messages.info(request, "Candidate already exists. No duplicate entry created.")

            # Process colleges applied
            college_names = extracted_data.get("colleges_applied", "").split(",")  # Assuming a comma-separated list
            
            for college_name in map(str.strip, college_names):
                if college_name:
                    # Check if application already exists for this candidate and college
                    existing_application = CollegeApplication.objects.filter(
                        candidate=candidate, college_name=college_name
                    ).exists()

                    if not existing_application:
                        CollegeApplication.objects.create(
                            candidate=candidate, college_name=college_name, application_status="pending"
                        )
            candidates = Candidate.objects.all()  # Fetch all candidates
            applications = CollegeApplication.objects.all()  # Fetch all applications

            return render(request, "officer_dashboard.html", {
                "form": form,
                "extracted_text": extracted_text,
                "processed_data": extracted_data,
                "candidates": candidates,  # Pass updated candidate list
                "applications": applications,  # Pass updated college applications
            })
    else:
        form = DocumentUploadForm()

    return render(request, "upload_document.html", {"form": form})


def add_candidate(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        program_fit = request.POST.get("program_fit")
        gpa = request.POST.get("gpa")
        shortlisted = request.POST.get("shortlisted") == "on"  # Convert checkbox to boolean
        academic_experience = request.POST.get("academic_experience", "").strip()
        skills = request.POST.get("skills", "").strip()
        projects = request.POST.get("projects", "").strip()

        # Extract multiple colleges and statuses from the form
        college_names = request.POST.getlist("college_name[]")  # Get list of college names
        application_statuses = request.POST.getlist("application_status[]")  # Get list of statuses

        # Check if the candidate already exists
        if Candidate.objects.filter(email=email).exists():
            messages.error(request, "A candidate with this email already exists.")
            return redirect("officer_dashboard")

        # Create a new candidate
        candidate = Candidate.objects.create(
            name=name,
            email=email,
            program_fit=program_fit,
            gpa=gpa,
            shortlisted=shortlisted,
            academic_experience=academic_experience,
            skills=skills,
            projects=projects
        )

        # Create CollegeApplication entries for each selected college
        for college_name, application_status in zip(college_names, application_statuses):
            CollegeApplication.objects.create(
                candidate=candidate,
                college_name=college_name.strip(),
                application_status=application_status
            )

        messages.success(request, "Candidate and applications added successfully!")
        return redirect("officer_dashboard")  # Redirect after successful submission

    return render(request, "officer_dashboard.html")

def candidate_profile(request, candidate_id):
    candidate = get_object_or_404(Candidate, id=candidate_id)
    return render(request, "candidate_profile.html", {"candidate": candidate})

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Candidate, CollegeApplication

def edit_candidate(request, candidate_id):
    candidate = get_object_or_404(Candidate, id=candidate_id)

    if request.method == "POST":
        # Update candidate details
        candidate.name = request.POST.get("name", "").strip()
        candidate.email = request.POST.get("email", "").strip()
        candidate.program_fit = request.POST.get("program_fit", "").strip()
        
        # Ensure GPA is correctly handled (convert to float, default to 0.0 if invalid)
        try:
            candidate.gpa = float(request.POST.get("gpa", candidate.gpa))
        except ValueError:
            candidate.gpa = candidate.gpa  # Keep existing GPA if input is invalid

        candidate.academic_experience = request.POST.get("academic_experience", "").strip()
        candidate.skills = request.POST.get("skills", "").strip()
        candidate.projects = request.POST.get("projects", "").strip()
        candidate.save()

        # Update college applications
        college_names = request.POST.getlist("college_name[]")  # List of colleges
        application_statuses = request.POST.getlist("application_status[]")  # List of statuses

        # Remove old applications and add new ones
        candidate.applications.all().delete()
        for college_name, application_status in zip(college_names, application_statuses):
            if college_name.strip():  # Ensure not empty
                CollegeApplication.objects.create(
                    candidate=candidate,
                    college_name=college_name.strip(),
                    application_status=application_status.strip()
                )

        messages.success(request, "Candidate details updated successfully!")
        return redirect("candidate_profile", candidate_id=candidate.id)

    return render(request, "edit_candidate.html", {"candidate": candidate})


# from django.db.utils import IntegrityError
# from .models import Candidate

# # Pre-load Sample Candidates
# sample_candidates = [
#     {"name": "Alice Johnson", "email": "alice@example.com", "program_fit": "engineering", "scores": 90, "application_status": "pending"},
#     {"name": "Bob Smith", "email": "bob@example.com", "program_fit": "math", "scores": 85, "application_status": "accepted"},
#     {"name": "Charlie Brown", "email": "charlie@example.com", "program_fit": "science", "scores": 78, "application_status": "waitlisted"},
#     {"name": "Diana Prince", "email": "diana@example.com", "program_fit": "business", "scores": 92, "application_status": "accepted"},
#     {"name": "Ethan Hunt", "email": "ethan@example.com", "program_fit": "arts", "scores": 88, "application_status": "pending"},
# ]

# def load_sample_candidates():
#     try:
#         for candidate_data in sample_candidates:
#             Candidate.objects.get_or_create(**candidate_data)
#     except IntegrityError:
#         pass  # Ignore errors if the data already exists

# # Load candidates when the server starts
# load_sample_candidates()