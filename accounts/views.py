from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Count, Sum
from datasets.models import Dataset, Category
from accounts.models import Profile
import json
from datetime import datetime, timedelta

def is_admin(user):
    return user.is_authenticated and hasattr(user, 'profile') and user.profile.role == 'admin'

def login_view(request):
    if request.user.is_authenticated:
        return redirect('/')
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            if hasattr(user, 'profile') and user.profile.role == 'admin':
                return redirect('admin_portal:admin_dashboard')
            return redirect('home')
        else:
            messages.error(request, 'Invalid email or password.')
    return render(request, 'accounts/login.html')

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        role = request.POST.get('role', 'public')

        if not full_name or not email or not password1 or not password2:
            messages.error(request, 'All fields are required.')
        elif password1 != password2:
            messages.error(request, 'Passwords do not match.')
        elif len(password1) < 12:
            messages.error(request, 'Password must be at least 12 characters long.')
        elif User.objects.filter(username=email).exists():
            messages.error(request, 'An account with this email already exists.')
        else:
            name_parts = full_name.strip().split(' ', 1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ''
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name
            )
            profile = user.profile
            profile.role = role
            profile.save()
            messages.success(request, 'Account created successfully. Please log in.')
            return redirect('/accounts/login/')
    return render(request, 'accounts/signup.html')

def logout_view(request):
    logout(request)
    return redirect('home')
