from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .forms import RegisterForm, SignInForm
from .models import User
from .models import Candidate, Event, ActivityLog, CollegeApplication
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

from .forms import RegisterForm, SignInForm
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.contrib.auth import login
from .serializers import SignUpSerializer

class SignUpAPIView(generics.CreateAPIView):
    serializer_class = SignUpSerializer
    permission_classes = [permissions.AllowAny]   # endpoint is public

    def perform_create(self, serializer):
        user = serializer.save()
        login(self.request, user)                 # log them in immediately

    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)
        return Response({"detail": "Registration successful."}, status=201)
    
from .serializers import SignInSerializer

class SignInAPIView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = SignInSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            request,
            username=serializer.validated_data["username"],
            password=serializer.validated_data["password"],
        )

        if user is None:
            return Response(
                {"detail": "Invalid credentials."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        login(request, user)  # creates session cookie

        # You can customize this based on user.role if needed
        return Response({"detail": "Login successful.", "redirect": "/dashboard"}, status=200)

def home(request):
    return render(request, "home.html", {
        "register_form": RegisterForm(),
        "signin_form": SignInForm()
    })

def signup(request):
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

    return render(request, "home.html", {
        "register_form": form,
        "signin_form": SignInForm()  # Still pass it in
    })

def signin(request):
    if request.user.is_authenticated:
        return redirect("/dashboard")

    if request.method == "POST":
        form = SignInForm(request, data=request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"]
            )
            if user:
                login(request, user)
                messages.success(request, "Login successful.")
                return redirect("/dashboard")
            else:
                messages.error(request, "Invalid credentials.")
    else:
        form = SignInForm()

    return render(request, "home.html", {
        "register_form": RegisterForm(),
        "signin_form": form
    })

from rest_framework.decorators import api_view
@api_view(["POST"])
def logout_view(request):
    logout(request)
    return Response({"message": "Logged out successfully."})

def is_admin(user):
    return user.role == "admin"

def is_officer(user):
    return user.role == "officer"

@login_required
@user_passes_test(lambda u: u.role == "admin")
def admin_dashboard(request):
    officers = User.objects.filter(role="officer").prefetch_related("candidates")  # Fetch all officers with their candidates
    logs = ActivityLog.objects.all()

    return render(request, "admin_dashboard.html", {
        "officers": officers,
        "logs": logs,
    })

def normalize_text(text):
    """Normalize text by removing spaces, underscores, and converting to lowercase."""
    return re.sub(r'[\s_]+', '', text).lower()

def calculate_score(self):
    score = 0

    # GPA weight (max 30)
    if self.gpa:
        score += min(self.gpa / 4.0 * 30, 30)

    # Skills weight (max 20)
    if self.skills:
        skills_list = [s.strip() for s in self.skills.split(",") if s.strip()]
        score += min(len(skills_list) * 2, 20)

    # Projects weight (max 20)
    if self.projects:
        project_count = self.projects.count("\n") + 1 if "\n" in self.projects else 1
        score += min(project_count * 5, 20)

    # Academic experience weight (max 30)
    if self.academic_experience:
        score += min(len(self.academic_experience.split()) / 10, 30)

    return round(score, 1)

# import spacy
# from spacy.util import is_package
# import spacy.cli
# def ensure_spacy_model(model_name="en_core_web_sm"):
#     if not is_package(model_name):
#         try:
#             spacy.cli.download(model_name)
#         except Exception as e:
#             raise RuntimeError(f"Failed to download spaCy model '{model_name}': {e}")
#     spacy.load(model_name)
# import nltk

# def ensure_nltk_corpora():
#     for corpus in ["stopwords", "words"]:
#         try:
#             nltk.data.find(f"corpora/{corpus}")
#         except LookupError:
#             print(f"Downloading NLTK corpus: {corpus}")
#             nltk.download(corpus)


            
# @login_required
# @user_passes_test(is_officer)
# def officer_dashboard(request):
#     print(">>> officer_dashboard loaded with method:", request.method)
#     program_fit_filter = request.GET.get("program_fit", "")
#     application_status_filter = request.GET.get("application_status", "")
#     college_filter = request.GET.get("college_name", "")
#     score_sort = request.GET.get("score_sort", "")
#     officers = User.objects.filter(role="officer")
#     candidates = Candidate.objects.filter(officer=request.user)
#     events = Event.objects.all().order_by("-date")
#     form = DocumentUploadForm()  # <-- Move here to ensure it's always defined

#     extracted_data = None
#     if request.method == "POST":
#         form = DocumentUploadForm(request.POST, request.FILES)
#         if form.is_valid():
#             try:
#                 ensure_spacy_model()
#                 ensure_nltk_corpora()
#                 from pydparser import ResumeParser
#             except Exception as e:
#                 messages.error(request, f"Model download error: {e}")
#                 return render(request, "upload.html", {"form": form})
#             uploaded_files = request.FILES.getlist('files')
#             for uploaded_file in uploaded_files:
#                 fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'uploads'))
#                 filename = fs.save(uploaded_file.name, uploaded_file)
#                 file_path = fs.path(filename)

#                 # Use pyresparser to extract structured resume data
#                 try:
#                     print(f">>> Attempting to parse: {file_path}")
#                     parsed_data = ResumeParser(file_path).get_extracted_data()
#                 except Exception as e:
#                     messages.error(request, f"Resume parsing failed for {uploaded_file.name}: {e}")
#                     print(">>> ResumeParser error:", e)
#                     continue

#                 # Map parsed fields to your existing format (you may need to customize this)
#                 extracted_data = {
#                     "name": parsed_data.get("name", ""),
#                     "email": parsed_data.get("email", ""),
#                     "gpa": parsed_data.get("cgpa", 0),
#                     "program": parsed_data.get("degree", [""])[0] if parsed_data.get("degree") else "",
#                     "academic_experience": "; ".join(parsed_data.get("experience", [])) if parsed_data.get("experience") else "",
#                     "skills": ", ".join(parsed_data.get("skills", [])) if parsed_data.get("skills") else "",
#                     "projects": "",  # pyresparser doesn't extract this directly; may need NLP/custom logic
#                     "colleges_applied": ""  # same as above
#                 }
#                 # Convert GPA to float safely
#                 gpa_value = None
#                 try:
#                     gpa_value = float(extracted_data["gpa"])
#                 except ValueError:
#                     gpa_value = None

#                 try:
#                     # Ensure candidate is saved in DB
#                     candidate, created = Candidate.objects.update_or_create(
#                         name=extracted_data["name"].replace("Name: ", ""),
#                         defaults={
#                             "email": extracted_data["email"], 
#                             "gpa": gpa_value,
#                             "program_fit": extracted_data["program"],
#                             "application_status": "pending",
#                             "academic_experience": extracted_data["academic_experience"], 
#                             "skills": extracted_data["skills"],                            
#                             "projects": extracted_data["projects"],
#                             "officer": request.user
#                         }
#                     )

#                     # Save colleges applied (ensure no duplicates)
#                     college_names = extracted_data.get("colleges_applied", "").split(",")

#                     for college_name in map(str.strip, college_names):
#                         if college_name:
#                             CollegeApplication.objects.get_or_create(
#                                 candidate=candidate,
#                                 college_name=college_name,
#                                 defaults={"application_status": "pending"}
#                             )
#                     if created:
#                         messages.success(request, "Candidate details extracted and saved successfully!")
#                     else:
#                         messages.info(request, "Candidate already exists. Updated existing entry.")

#                 except IntegrityError as e:
#                     print("Database error:", e)
#                     messages.error(request, "Error saving candidate data. Please check for duplicates.")

#                 candidates = Candidate.objects.filter(officer=request.user)
#                 officers = User.objects.filter(role="officer")
    
#     events = Event.objects.all().order_by("-date")
#     print(">>> Loaded events:", list(events))
    
#     # if program_fit_filter:
#     #     normalized_filter = normalize_text(program_fit_filter)
#     #     candidates = candidates.filter(program_fit__icontains=normalized_filter)

#     program_fit_filter = request.GET.get("program_fit", "")
#     candidates = Candidate.objects.filter(officer=request.user)

#     if program_fit_filter:
#         # Convert snake_case → space-separated for partial match
#         keyword = program_fit_filter.replace("_", " ").lower()
#         candidates = candidates.filter(program_fit__icontains=keyword)

#     if application_status_filter:
#         candidates = candidates.filter(applications__application_status=application_status_filter)
#     if college_filter:
#         candidates = candidates.filter(applications__college_name__icontains=college_filter).distinct()
#     if score_sort == "high_to_low":
#         candidates = candidates.order_by(F("gpa").desc())
#     elif score_sort == "low_to_high":
#         candidates = candidates.order_by(F("gpa").asc())
    
#     for c in candidates:
#         c.score = c.calculate_score()
#     return render(request, "officer_dashboard.html", {
#         "candidates": candidates,
#         "events": events,
#         "form": form,
#         "extracted_data": extracted_data,
#         "officers": officers,
#         "program_choices": Candidate.PROGRAM_CHOICES
#     })
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status

from django.db.models import F
from django.db import IntegrityError
from django.conf import settings
from django.core.files.storage import FileSystemStorage

from .models import Candidate, Event, CollegeApplication, User
from .serializers import CandidateSerializer, EventSerializer, OfficerSerializer
from .forms import DocumentUploadForm

import os

from pydparser import ResumeParser


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_data(request):
    user = request.user
    program_fit_filter = request.GET.get("program_fit", "")
    application_status_filter = request.GET.get("application_status", "")
    college_filter = request.GET.get("college_name", "")
    score_sort = request.GET.get("score_sort", "")

    candidates = Candidate.objects.filter(officer=user)

    if program_fit_filter:
        keyword = program_fit_filter.replace("_", " ").lower()
        candidates = candidates.filter(program_fit__icontains=keyword)

    if application_status_filter:
        candidates = candidates.filter(applications__application_status=application_status_filter)
    if college_filter:
        candidates = candidates.filter(applications__college_name__icontains=college_filter).distinct()
    if score_sort == "high_to_low":
        candidates = candidates.order_by(F("gpa").desc())
    elif score_sort == "low_to_high":
        candidates = candidates.order_by(F("gpa").asc())

    for c in candidates:
        c.score = c.calculate_score()

    events = Event.objects.all().order_by("-date")
    officers = User.objects.filter(role="officer")

    return Response({
        "candidates": CandidateSerializer(candidates, many=True).data,
        "events": EventSerializer(events, many=True).data,
        "officers": OfficerSerializer(officers, many=True).data,
        "program_choices": Candidate.PROGRAM_CHOICES
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_resume(request):
    # form = DocumentUploadForm(request.data, request.FILES)
    # if not form.is_valid():
    #     return Response({"error": "Invalid form."}, status=400)

    # try:
    #     ensure_spacy_model()
    #     ensure_nltk_corpora()
    # except Exception as e:
    #     return Response({"error": f"Model download error: {str(e)}"}, status=500)

    # uploaded_files = request.FILES.getlist('files')
    # results = []

    # for uploaded_file in uploaded_files:
    #     fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'uploads'))
    #     filename = fs.save(uploaded_file.name, uploaded_file)
    #     file_path = fs.path(filename)

    #     try:
    #         parsed_data = ResumeParser(file_path).get_extracted_data()
    #     except Exception as e:
    #         return Response({"error": f"Resume parsing failed for {uploaded_file.name}: {e}"}, status=400)

    #     extracted = {
    #         "name": parsed_data.get("name", "").replace("Name: ", ""),
    #         "email": parsed_data.get("email", ""),
    #         "gpa": parsed_data.get("cgpa", 0),
    #         "program": parsed_data.get("degree", [""])[0] if parsed_data.get("degree") else "",
    #         "academic_experience": "; ".join(parsed_data.get("experience", [])) if parsed_data.get("experience") else "",
    #         "skills": ", ".join(parsed_data.get("skills", [])) if parsed_data.get("skills") else "",
    #         "projects": "",
    #         "colleges_applied": ""
    #     }

    #     # Convert GPA to float safely
    #     try:
    #         gpa_value = float(extracted["gpa"])
    #     except ValueError:
    #         gpa_value = None

    #     try:
    #         candidate, created = Candidate.objects.update_or_create(
    #             name=extracted["name"],
    #             defaults={
    #                 "email": extracted["email"],
    #                 "gpa": gpa_value,
    #                 "program_fit": extracted["program"],
    #                 "application_status": "pending",
    #                 "academic_experience": extracted["academic_experience"],
    #                 "skills": extracted["skills"],
    #                 "projects": extracted["projects"],
    #                 "officer": request.user
    #             }
    #         )

    #         college_names = extracted.get("colleges_applied", "").split(",")
    #         for college_name in map(str.strip, college_names):
    #             if college_name:
    #                 CollegeApplication.objects.get_or_create(
    #                     candidate=candidate,
    #                     college_name=college_name,
    #                     defaults={"application_status": "pending"}
    #                 )

    #         results.append({"candidate": candidate.name, "status": "created" if created else "updated"})

    #     except IntegrityError as e:
    #         return Response({"error": f"Database error: {e}"}, status=400)

    return Response({"message": "Resumes processed successfully", "results": results}, status=200)


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


# @login_required
# def send_message(request):
#     if request.method == "POST":
#         candidate_id = request.POST.get("candidate_id")
#         candidate = get_object_or_404(Candidate, id=candidate_id)
#         content = request.POST.get("content")
#         if content:
#             Message.objects.create(sender=request.user, receiver_email=candidate.email, content=content, timestamp=now())
#             messages.success(request, "Message sent successfully.")
#     return redirect("officer_dashboard")

# @login_required
# def send_message_to_user(request):
#     if request.method == "POST":
#         recipient_email = request.POST.get("recipient_email").strip()
#         content = request.POST.get("content").strip()

#         if not content:
#             messages.error(request, "Message content cannot be empty.")
#             return redirect("messages_page")

#         if not recipient_email:
#             messages.error(request, "Please select a recipient.")
#             return redirect("messages_page")

#         # Ensure the recipient exists in the system
#         recipient = User.objects.filter(email=recipient_email).first()
#         if not recipient:
#             messages.error(request, "Invalid recipient. User does not exist.")
#             return redirect("messages_page")

#         # Create and save the message
#         Message.objects.create(sender=request.user, receiver_email=recipient_email, content=content)
#         messages.success(request, f"Message sent to {recipient.username}.")

#     return redirect("messages_page")

# @login_required
# def message_page(request):
#     users = User.objects.exclude(id=request.user.id)  # Get all users except the logged-in user
#     candidates = Candidate.objects.filter(officer=request.user)  # Get all candidates

#     # Messages sent by the logged-in officer/admin
#     messages_sent = Message.objects.filter(sender=request.user).order_by("-timestamp")

#     # Messages received by the logged-in officer/admin
#     messages_received = Message.objects.filter(receiver_email=request.user.email).order_by("-timestamp")

#     # Separate messages between officers and between candidates
#     officer_sent_messages = messages_sent.filter(receiver_email__in=users.values_list('email', flat=True))
#     candidate_sent_messages = messages_sent.exclude(receiver_email__in=users.values_list('email', flat=True))

#     officer_received_messages = messages_received.filter(sender__in=users)
#     candidate_received_messages = messages_received.exclude(sender__in=users)

#     return render(request, "messages.html", {
#         "users": users,
#         "candidates": candidates,
#         "officer_sent_messages": officer_sent_messages,
#         "candidate_sent_messages": candidate_sent_messages,
#         "officer_received_messages": officer_received_messages,
#         "candidate_received_messages": candidate_received_messages,
#     })


@login_required
def dashboard(request):
    print("Logged in user:", request.user.username, "Role:", request.user.role)
    if request.user.role == "admin":
        return redirect("admin_dashboard")
    return redirect(("http://localhost:3000/officer_dashboard"))

# @login_required
# @user_passes_test(is_officer)
# def create_event(request):
#     if request.method == "POST":
#         title = request.POST.get("title")
#         description = request.POST.get("description")
#         date = request.POST.get("date")
#         if title and description and date:
#             Event.objects.create(title=title, description=description, date=date, created_by=request.user)
#             messages.success(request, "Event created successfully.")
#     return redirect("officer_dashboard")

# @login_required
# @user_passes_test(is_officer)
# def invite_candidate_to_event(request):
#     if request.method == "POST":
#         event_id = request.POST.get("event_id")
#         candidate_ids = request.POST.getlist("candidate_ids[]")  # Get multiple selected candidates

#         event = get_object_or_404(Event, id=event_id)

#         invited_candidates = []
#         for candidate_id in candidate_ids:
#             candidate = get_object_or_404(Candidate, id=candidate_id)
#             event.members.add(candidate)  # Add candidate to event
#             invited_candidates.append(candidate.name)

#         if invited_candidates:
#             messages.success(request, f"Invited {', '.join(invited_candidates)} to {event.title}.")
#         else:
#             messages.warning(request, "No candidates were selected.")

#     return redirect("officer_dashboard")

# @api_view(["POST"])
# @permission_classes([IsAuthenticated])
# def create_event_api(request):
#     if request.user.role != "officer":
#         return Response({"error": "Unauthorized"}, status=403)

#     title = request.data.get("title")
#     description = request.data.get("description")
#     date = request.data.get("date")

#     if not (title and description and date):
#         return Response({"error": "Missing fields"}, status=400)

#     event = Event.objects.create(title=title, description=description, date=date, created_by=request.user)
#     return Response({"message": "Event created", "event_id": event.id}, status=201)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_event_api(request):
    if request.user.role != "officer":
        return Response({"error": "Unauthorized"}, status=403)

    user = request.user
    data = request.data

    title = data.get("title")
    description = data.get("description")
    date = data.get("date")
    candidate_ids = data.get("candidate_ids", [])  # optional

    if not (title and description and date):
        return Response({"error": "Missing required fields."}, status=400)

    try:
        event = Event.objects.create(
            title=title,
            description=description,
            date=date,
            created_by=user
        )

        if candidate_ids:
            candidates = Candidate.objects.filter(id__in=candidate_ids)
            event.members.add(*candidates)

        return Response({"message": "Event created", "event_id": event.id}, status=201)

    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def invite_candidates_api(request):
    if request.user.role != "officer":
        return Response({"error": "Unauthorized"}, status=403)

    event_id = request.data.get("event_id")
    candidate_ids = request.data.get("candidate_ids", [])

    event = get_object_or_404(Event, id=event_id)
    invited = []

    for cid in candidate_ids:
        candidate = get_object_or_404(Candidate, id=cid)
        event.members.add(candidate)
        invited.append(candidate.name)

    return Response({"message": f"Invited {', '.join(invited)}"}, status=200)

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
    print("Extracting fields from text:", text[:300])
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


# @login_required
# @user_passes_test(is_officer)
# def upload_document(request):
#     if request.method == "POST":
#         form = DocumentUploadForm(request.POST, request.FILES)
#         if form.is_valid():
#             uploaded_files = form.cleaned_data["files"]
#             all_extracted_data = []

#             for uploaded_file in uploaded_files:
#                 fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'uploads'))
#                 filename = fs.save(uploaded_file.name, uploaded_file)
#                 file_path = fs.path(filename)

#                 # Extract text from file
#                 if uploaded_file.name.endswith(".pdf"):
#                     extracted_text = extract_text_from_pdf(file_path)
#                 elif uploaded_file.name.endswith(".docx"):
#                     extracted_text = extract_text_from_docx(file_path)
#                 else:
#                     messages.warning(request, f"Unsupported file: {uploaded_file.name}")
#                     continue

#                 extracted_data = process_extracted_text(extracted_text)
#                 all_extracted_data.append(extracted_data)

#                 try:
#                     gpa_value = float(extracted_data.get("gpa", 0.0))
#                 except ValueError:
#                     gpa_value = None

#                 candidate, created = Candidate.objects.get_or_create(
#                     email=extracted_data["email"],
#                     defaults={
#                         "name": extracted_data["name"],
#                         "gpa": gpa_value,
#                         "program_fit": extracted_data["program"],
#                         "academic_experience": extracted_data["academic_experience"],
#                         "skills": extracted_data["skills"],
#                         "projects": extracted_data["projects"],
#                         "officer": request.user
#                     }
#                 )
#                 if not created and candidate.officer is None:
#                     candidate.officer = request.user
#                     candidate.save()

#                 college_names = extracted_data.get("colleges_applied", "").split(",")
#                 for college_name in map(str.strip, college_names):
#                     if college_name:
#                         exists = CollegeApplication.objects.filter(
#                             candidate=candidate,
#                             college_name=college_name
#                         ).exists()
#                         if not exists:
#                             CollegeApplication.objects.create(
#                                 candidate=candidate,
#                                 college_name=college_name,
#                                 application_status="pending"
#                             )

#             candidates = Candidate.objects.filter(officer=request.user)
#             applications = CollegeApplication.objects.all()

#             messages.success(request, "All files processed successfully.")
#             return render(request, "officer_dashboard.html", {
#                 "form": form,
#                 "processed_data_list": all_extracted_data,
#                 "candidates": candidates,
#                 "applications": applications
#             })
#     else:
#         form = DocumentUploadForm()

#     candidates = Candidate.objects.filter(officer=request.user)
#     applications = CollegeApplication.objects.all()
#     return render(request, "officer_dashboard.html", {
#         "form": form,
#         "candidates": candidates,
#         "applications": applications
#     })

@api_view(["POST"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser])
def upload_document_api(request):
    if not request.user.role == "officer":
        return Response({"error": "Permission denied."}, status=403)

    form = DocumentUploadForm(request.data, request.FILES)
    if not form.is_valid():
        return Response({"error": "Invalid form submission."}, status=400)

    uploaded_files = form.cleaned_data["files"]
    processed_data = []

    for uploaded_file in uploaded_files:
        fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, "uploads"))
        filename = fs.save(uploaded_file.name, uploaded_file)
        file_path = fs.path(filename)

        if uploaded_file.name.endswith(".pdf"):
            text = extract_text_from_pdf(file_path)
        elif uploaded_file.name.endswith(".docx"):
            text = extract_text_from_docx(file_path)
        else:
            print(f"Skipped unsupported file: {uploaded_file.name}")
            continue  # skip unsupported file types
        print(f"Processing file: {uploaded_file.name}")

        extracted = process_extracted_text(text)
        print("Extracted Info:", extracted)
        normalized = {
            "name": extracted.get("name", ""),
            "email": extracted.get("email", ""),
            "program_fit": extracted.get("program", ""),  # renamed key for frontend
            "gpa": extracted.get("gpa", ""),
            "academic_experience": extracted.get("academic_experience", ""),
            "skills": extracted.get("skills", ""),
            "projects": extracted.get("projects", ""),
            "colleges_applied": extracted.get("colleges_applied", "")
        }
        processed_data.append(normalized)

        # Try parsing GPA
        try:
            gpa_value = float(extracted.get("gpa", 0.0))
        except ValueError:
            gpa_value = None

        candidate, created = Candidate.objects.get_or_create(
            email=extracted["email"],
            defaults={
                "name": extracted["name"],
                "gpa": gpa_value,
                "program_fit": extracted["program"],
                "academic_experience": extracted["academic_experience"],
                "skills": extracted["skills"],
                "projects": extracted["projects"],
                "officer": request.user
            }
        )

        if not created and candidate.officer is None:
            candidate.officer = request.user
            candidate.save()

        colleges = extracted.get("colleges_applied", "").split(",")
        for college in map(str.strip, colleges):
            if college:
                if not CollegeApplication.objects.filter(candidate=candidate, college_name=college).exists():
                    CollegeApplication.objects.create(
                        candidate=candidate,
                        college_name=college,
                        application_status="pending"
                    )

    return Response({"message": "Files processed", "results": processed_data}, status=201)

# @login_required
# @user_passes_test(is_officer)
# def add_candidate(request):
#     if request.method == "POST":
#         name = request.POST.get("name")
#         email = request.POST.get("email")
#         program_fit = request.POST.get("program_fit")
#         gpa = request.POST.get("gpa")
#         shortlisted = request.POST.get("shortlisted") == "on"  # Convert checkbox to boolean
#         academic_experience = request.POST.get("academic_experience", "").strip()
#         skills = request.POST.get("skills", "").strip()
#         projects = request.POST.get("projects", "").strip()

#         # Extract multiple colleges and statuses from the form
#         college_names = request.POST.getlist("college_name[]")
#         application_statuses = request.POST.getlist("application_status[]")

#         # Get the selected officer
#         officer_id = request.POST.get("officer")
#         officer = User.objects.filter(id=officer_id, role="officer").first()

#         if not officer:
#             messages.error(request, "Invalid officer selection.")
#             return redirect("add_candidate")

#         # Check if the candidate already exists
#         if Candidate.objects.filter(email=email).exists():
#             messages.error(request, "A candidate with this email already exists.")
#             return redirect("officer_dashboard")

#         # Create a new candidate assigned to the selected officer
#         candidate = Candidate.objects.create(
#             name=name,
#             email=email,
#             program_fit=program_fit,
#             gpa=gpa,
#             shortlisted=shortlisted,
#             academic_experience=academic_experience,
#             skills=skills,
#             projects=projects,
#             officer=officer  # Assign chosen officer
#         )

#         # Create CollegeApplication entries for each selected college
#         for college_name, application_status in zip(college_names, application_statuses):
#             CollegeApplication.objects.create(
#                 candidate=candidate,
#                 college_name=college_name.strip(),
#                 application_status=application_status
#             )

#         messages.success(request, "Candidate and applications added successfully!")
#         return redirect("officer_dashboard")

#     # Get all officers to display in the dropdown
#     officers = User.objects.filter(role="officer")
#     print("Officers passed to template:", officers)
#     return render(request, "officer_dashboard.html", {"officers": officers})

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_candidate(request):
    if not request.user.role == "officer":
        return Response({"error": "Permission denied."}, status=403)

    data = request.data

    name = data.get("name")
    email = data.get("email")
    program_fit = data.get("program_fit")
    gpa = data.get("gpa")
    shortlisted = data.get("shortlisted", False)
    academic_experience = data.get("academic_experience", "").strip()
    skills = data.get("skills", "").strip()
    projects = data.get("projects", "").strip()

    college_names = data.get("college_name", [])  # list
    application_statuses = data.get("application_status", [])  # list
    officer_id = data.get("officer")

    if not (name and email and officer_id):
        return Response({"error": "Missing required fields."}, status=400)

    officer = User.objects.filter(id=officer_id, role="officer").first()
    if not officer:
        return Response({"error": "Invalid officer selected."}, status=400)

    if Candidate.objects.filter(email=email).exists():
        return Response({"error": "Candidate with this email already exists."}, status=400)

    try:
        candidate = Candidate.objects.create(
            name=name,
            email=email,
            program_fit=program_fit,
            gpa=gpa,
            shortlisted=shortlisted,
            academic_experience=academic_experience,
            skills=skills,
            projects=projects,
            officer=officer
        )

        for college_name, status_str in zip(college_names, application_statuses):
            CollegeApplication.objects.create(
                candidate=candidate,
                college_name=college_name.strip(),
                application_status=status_str
            )

        return Response({"message": "Candidate and applications added successfully!"}, status=201)

    except IntegrityError as e:
        return Response({"error": str(e)}, status=500)

def candidate_profile(request, candidate_id):
    candidate = get_object_or_404(Candidate, id=candidate_id)
    return render(request, "candidate_profile.html", {"candidate": candidate})

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Candidate, CollegeApplication

@login_required
@user_passes_test(is_officer)
def edit_candidate(request, candidate_id):
    candidate = get_object_or_404(Candidate, id=candidate_id, officer=request.user)  # Only allow editing their own candidates

    if request.method == "POST":
        candidate.name = request.POST.get("name", "").strip()
        candidate.email = request.POST.get("email", "").strip()
        candidate.program_fit = request.POST.get("program_fit", "").strip()
        
        try:
            candidate.gpa = float(request.POST.get("gpa", candidate.gpa))
        except ValueError:
            candidate.gpa = candidate.gpa

        candidate.academic_experience = request.POST.get("academic_experience", "").strip()
        candidate.skills = request.POST.get("skills", "").strip()
        candidate.projects = request.POST.get("projects", "").strip()
        candidate.save()

        # **Handle College Applications**
        college_names = request.POST.getlist("college_name[]")  # List of college names
        application_statuses = request.POST.getlist("application_status[]")  # Corresponding statuses

        # **Clear old applications before adding updated ones**
        candidate.applications.all().delete()  

        # **Save new college applications**
        for college_name, application_status in zip(college_names, application_statuses):
            if college_name.strip():  # Ensure not empty
                CollegeApplication.objects.create(
                    candidate=candidate,
                    college_name=college_name.strip(),
                    application_status=application_status.strip()
                )

        messages.success(request, "Candidate details and colleges applied updated successfully!")
        return redirect("candidate_profile", candidate_id=candidate.id)

    return render(request, "edit_candidate.html", {"candidate": candidate})

from django.shortcuts import render
from .models import Candidate, CollegeApplication

# @login_required
# @user_passes_test(lambda u: u.role == "officer")
# def statistics_view(request):
#     filter_option = request.GET.get("filter", "mine")  # Default to 'mine' for officers

#     if filter_option == "mine":
#         candidates = Candidate.objects.filter(officer=request.user)
#     else:
#         candidates = Candidate.objects.all()

#     total_candidates = candidates.count()
#     applications = CollegeApplication.objects.filter(candidate__in=candidates)

#     total_college_applications = applications.count()
#     accepted_college_applications = applications.filter(application_status="accepted").count()
#     rejected_college_applications = applications.filter(application_status="rejected").count()
#     pending_college_applications = applications.filter(application_status="pending").count()
#     waitlisted_college_applications = applications.filter(application_status="waitlisted").count()

#     if total_college_applications > 0:
#         acceptance_ratio = round((accepted_college_applications / total_college_applications) * 100, 2)
#     else:
#         acceptance_ratio = 0

#     # Per-candidate acceptance stats
#     candidate_acceptance_ratios = []
#     for candidate in candidates:
#         candidate_apps = candidate.applications.all()
#         total = candidate_apps.count()
#         accepted = candidate_apps.filter(application_status="accepted").count()
#         ratio = round((accepted / total) * 100, 2) if total > 0 else 0

#         candidate_acceptance_ratios.append({
#             "name": candidate.name,
#             "total_applications": total,
#             "accepted_applications": accepted,
#             "acceptance_ratio": ratio
#         })

#     context = {
#         "total_candidates": total_candidates,
#         "total_college_applications": total_college_applications,
#         "accepted_college_applications": accepted_college_applications,
#         "rejected_college_applications": rejected_college_applications,
#         "pending_college_applications": pending_college_applications,
#         "waitlisted_college_applications": waitlisted_college_applications,
#         "acceptance_ratio": acceptance_ratio,
#         "candidate_acceptance_ratios": candidate_acceptance_ratios,
#         "filter": filter_option
#     }

#     return render(request, "statistics.html", context)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Candidate, CollegeApplication

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def statistics_api(request):
    filter_option = request.GET.get("filter", "mine")

    if filter_option == "mine":
        candidates = Candidate.objects.filter(officer=request.user)
    else:
        candidates = Candidate.objects.all()

    total_candidates = candidates.count()
    applications = CollegeApplication.objects.filter(candidate__in=candidates)

    total_college_applications = applications.count()
    accepted = applications.filter(application_status="accepted").count()
    rejected = applications.filter(application_status="rejected").count()
    pending = applications.filter(application_status="pending").count()
    waitlisted = applications.filter(application_status="waitlisted").count()

    acceptance_ratio = round((accepted / total_college_applications) * 100, 2) if total_college_applications else 0

    candidate_ratios = []
    for c in candidates:
        apps = c.applications.all()
        total = apps.count()
        acc = apps.filter(application_status="accepted").count()
        ratio = round((acc / total) * 100, 2) if total else 0
        candidate_ratios.append({
            "name": c.name,
            "total_applications": total,
            "accepted_applications": acc,
            "acceptance_ratio": ratio
        })

    return Response({
        "filter": filter_option,
        "total_candidates": total_candidates,
        "total_college_applications": total_college_applications,
        "accepted": accepted,
        "rejected": rejected,
        "pending": pending,
        "waitlisted": waitlisted,
        "acceptance_ratio": acceptance_ratio,
        "candidate_acceptance_ratios": candidate_ratios,
    })

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_events_api(request):
    events = Event.objects.all().order_by("-date")
    serialized = EventSerializer(events, many=True)
    return Response(serialized.data)

from .serializers import CandidateListSerializer

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_candidates_api(request):
    user = request.user
    candidates = Candidate.objects.filter(officer=user)

    # Filters
    program_fit = request.GET.get("program_fit", "")
    application_status = request.GET.get("application_status", "")
    college_name = request.GET.get("college_name", "")
    score_sort = request.GET.get("score_sort", "")

    if program_fit:
        candidates = candidates.filter(program_fit__icontains=program_fit.replace("_", " "))

    if application_status:
        candidates = candidates.filter(applications__application_status=application_status)

    if college_name:
        candidates = candidates.filter(applications__college_name__icontains=college_name).distinct()

    if score_sort == "high_to_low":
        candidates = candidates.order_by(F("gpa").desc(nulls_last=True))
    elif score_sort == "low_to_high":
        candidates = candidates.order_by(F("gpa").asc(nulls_last=True))

    # Attach score dynamically
    for c in candidates:
        c.score = c.calculate_score()

    serialized = CandidateListSerializer(candidates, many=True)
    return Response({
        "candidates": serialized.data,
        "program_choices": Candidate.PROGRAM_CHOICES
    })

from django.http import JsonResponse
from django.contrib.auth import get_user_model

def officer_list(request):
    User = get_user_model()
    officers = User.objects.filter(role="officer").values("id", "username", "email")
    return JsonResponse(list(officers), safe=False)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_message_recipients(request):
    User = get_user_model()

    officers = User.objects.filter(role="officer").values("id", "username").annotate(role_label=models.Value("officer", output_field=models.CharField()))
    candidates = Candidate.objects.all().values("id", "name").annotate(role_label=models.Value("candidate", output_field=models.CharField()))

    combined = [
        {"id": o["id"], "username": o["username"], "role": o["role_label"]}
        for o in officers
    ] + [
        {"id": c["id"], "username": c["name"], "role": c["role_label"]}
        for c in candidates
    ]

    return Response(combined)

@login_required
@api_view(["GET"])
def profile_view(request):
    user = request.user

    try:
        photo_url = user.profile_photo.url if user.profile_photo else ""
    except Exception:
        photo_url = ""

    return Response({
        "username": user.username,
        "email": user.email,
        "role_display": user.get_role_display(),
        "job_title": user.job_title or "",
        "photo_url": photo_url,
            })
from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
@api_view(["POST"])
@login_required
def upload_photo(request):
    user = request.user
    if "photo" in request.FILES:
        user.profile_photo = request.FILES["photo"]
        user.save()
        return Response({"photo_url": user.profile_photo.url})
    return Response({"error": "No file uploaded"}, status=400)

# views.py

from .models import Message_new
from .serializers import MessageSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class MessageListCreateView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Message_new.objects.filter(
            Q(sender=user) | Q(recipient=user)
        ).order_by('-sent_at').select_related('sender', 'recipient')

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

class MessageMarkAsReadView(generics.UpdateAPIView):
    queryset = Message_new.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_update(self, serializer):
        serializer.save(is_read=True, read_at=now())