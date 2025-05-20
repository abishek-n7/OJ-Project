from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from .models import UserProfile

def user_profile(request):
    return render(request, 'user_profile.html')

