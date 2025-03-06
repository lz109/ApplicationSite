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
        candidates = candidates.filter(program_fit=program_fit_filter)
    if application_status_filter:
        candidates = candidates.filter(application_status=application_status_filter)
    if score_sort == "high_to_low":
        candidates = candidates.order_by(F("scores").desc())
    elif score_sort == "low_to_high":
        candidates = candidates.order_by(F("scores").asc())
    
    return render(request, "officer_dashboard.html", {"candidates": candidates, "events": events})

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

# Logger setup (can be placed in a separate logging configuration file)
logger = logging.getLogger(__name__)
logging.basicConfig(filename="logs/system.log", level=logging.INFO)

def log_event(message):
    logger.info(message)




from django.db.utils import IntegrityError
from .models import Candidate

# Pre-load Sample Candidates
sample_candidates = [
    {"name": "Alice Johnson", "email": "alice@example.com", "program_fit": "engineering", "scores": 90, "application_status": "pending"},
    {"name": "Bob Smith", "email": "bob@example.com", "program_fit": "math", "scores": 85, "application_status": "accepted"},
    {"name": "Charlie Brown", "email": "charlie@example.com", "program_fit": "science", "scores": 78, "application_status": "waitlisted"},
    {"name": "Diana Prince", "email": "diana@example.com", "program_fit": "business", "scores": 92, "application_status": "accepted"},
    {"name": "Ethan Hunt", "email": "ethan@example.com", "program_fit": "arts", "scores": 88, "application_status": "pending"},
]

def load_sample_candidates():
    try:
        for candidate_data in sample_candidates:
            Candidate.objects.get_or_create(**candidate_data)
    except IntegrityError:
        pass  # Ignore errors if the data already exists

# Load candidates when the server starts
load_sample_candidates()