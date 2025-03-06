from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .forms import RegisterForm, SignInForm
from .models import User
from .models import Candidate, Message, Event, ActivityLog
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import UserProfileForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q, F
from django.utils.timezone import now

from .forms import EditProfileForm
from .forms import AddOfficerForm
import logging

import fitz  # PyMuPDF
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

@login_required
@user_passes_test(is_officer)
def officer_dashboard(request):
    program_fit_filter = request.GET.get("program_fit", "")
    application_status_filter = request.GET.get("application_status", "")
    score_sort = request.GET.get("score_sort", "")

    candidates = Candidate.objects.all()
    events = Event.objects.all().order_by("-date")

    if program_fit_filter:
        candidates = candidates.filter(program_fit__iexact=program_fit_filter)
    if application_status_filter:
        candidates = candidates.filter(application_status=application_status_filter)
    if score_sort == "high_to_low":
        candidates = candidates.order_by(F("scores").desc())
    elif score_sort == "low_to_high":
        candidates = candidates.order_by(F("scores").asc())

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
    candidate = get_object_or_404(Candidate, id=candidate_id)

    if request.method == "POST":
        new_status = request.POST.get("application_status")  # Get new_status from form

        if new_status in ["pending", "accepted", "rejected"]:
            old_status = candidate.application_status
            candidate.application_status = new_status
            candidate.save()

            # Log the officer's action
            ActivityLog.objects.create(
                officer=request.user,
                action=f"changed status from {old_status} to {new_status}",
                candidate=candidate
            )

            messages.success(request, f"Candidate {candidate.name} status updated to {new_status}.")
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
def message_page(request):
    messages_received = Message.objects.filter(receiver_email=request.user.email).order_by("-timestamp")
    messages_sent = Message.objects.filter(sender=request.user).order_by("-timestamp")
    return render(request, "messages.html", {"messages_received": messages_received, "messages_sent": messages_sent})

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
        candidate_id = request.POST.get("candidate_id")

        event = get_object_or_404(Event, id=event_id)
        candidate = get_object_or_404(Candidate, id=candidate_id)

        event.members.add(candidate)
        messages.success(request, f"{candidate.name} has been invited to {event.title}.")

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

def process_extracted_text(text):
    # Find email
    email_match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    email = email_match.group(0) if email_match else "Not Found"

    # Find GPA 
    gpa_match = re.search(r"GPA[:\-\s]+(\d\.\d)", text, re.IGNORECASE)
    gpa = gpa_match.group(1) if gpa_match else "Not Found"

    # Find program 
    program_match = re.search(r"Program[:\-\s]+([\w\s]+)", text, re.IGNORECASE)
    program = program_match.group(1).strip() if program_match else "Not Found"

    # Find full name
    name_match = re.search(r"Name[:\-\s]+([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)\n", text)
    name = name_match.group(1) if name_match else "Not Found"

    return {
        "name": name,
        "email": email,
        "gpa": gpa,
        "program": program
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
                    "program_fit": extracted_data["program"]
                }
            )

            if created:
                messages.success(request, "Candidate details extracted and saved successfully!")
            else:
                messages.info(request, "Candidate already exists. No duplicate entry created.")

            return render(request, "upload_document.html", {"form": form, "extracted_text": extracted_text, "processed_data": extracted_data})

    else:
        form = DocumentUploadForm()

    return render(request, "upload_document.html", {"form": form})


def add_candidate(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        program_fit = request.POST.get("program_fit")
        gpa = request.POST.get("gpa")
        application_status = request.POST.get("application_status")
        shortlisted = request.POST.get("shortlisted") == "on"  # Convert checkbox to boolean

        # Check if email already exists (to prevent duplicates)
        if Candidate.objects.filter(email=email).exists():
            messages.error(request, "A candidate with this email already exists.")
            return redirect("officer_dashboard")  # Redirect back to the form

        # Create new candidate
        Candidate.objects.create(
            name=name,
            email=email,
            program_fit=program_fit,
            gpa=gpa,
            application_status=application_status,
            shortlisted=shortlisted
        )

        messages.success(request, "Candidate added successfully!")
        return redirect("officer_dashboard")  # Redirect after successful submission

    return render(request, "officer_dashboard.html")


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