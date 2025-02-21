from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .forms import RegisterForm, SignInForm
from .models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import UserProfileForm


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
    return render(request, "officer_dashboard.html")

@login_required
def dashboard(request):
    if request.user.role == "admin":
        return redirect("admin_dashboard")
    return redirect("officer_dashboard")

@login_required
def view_profile(request):
    return render(request, "profile.html", {"user": request.user})

@login_required
def update_profile(request):
    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("view_profile")
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, "edit_profile.html", {"form": form})
