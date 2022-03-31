from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from .models import *
# --------------- generate token --------------
import uuid
# ----------------email------------------------
from django.conf import settings
from django.template.loader import get_template
from django.core.mail import EmailMessage


# Create your views here.

@login_required(login_url='login')
def home(request):
    return render(request, 'home.html')


def loginUser(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user_obj = User.objects.filter(username=username).first()
        if user_obj is None:
            messages.error(request, 'User not found.')
            return redirect('login')
        profile_obj = Profile.objects.filter(user=user_obj).first()
        if not profile_obj.is_verified:  # check if user not verify yet
            messages.error(request, 'User is not verified check your email.')
            return redirect('login')
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
    return render(request, 'login.html')


def logoutUser(request):
    logout(request)
    return redirect('login')


def token_send(request):
    return render(request, 'token_sent.html')


def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
    try:
        if User.objects.filter(username=username).first():
            messages.error(request, 'Username is taken.')
            return redirect('register')

        if User.objects.filter(email=email).first():
            messages.error(request, 'Email is taken.')
            return redirect('register')
        user_obj = User.objects.create(username=username, email=email)
        user_obj.set_password(password)
        user_obj.save()
        auth_token = str(uuid.uuid4())
        profile_obj = Profile.objects.create(user=user_obj, auth_token=auth_token)
        profile_obj.save()
        sent_mail_after_registration(request, email, auth_token)
        return redirect('token_send')
    except Exception as e:
        print(e)
    return render(request, 'register.html')


def success(request):
    return render(request, 'success.html')


def sent_mail_after_registration(request, email, auth_token):

    subject = 'Verify Imformation'
    domain = get_current_site(request).domain
    html_content = get_template("email_template.html").render({'auth_token': auth_token, 'domain': domain})
    to = email
    try:
        email = EmailMessage(
            subject,
            html_content,
            settings.APPLICATION_EMAIL,
            [to],
            headers={'Message-ID': 'foo'},
        )
        email.content_subtype = 'html'
        email.send(fail_silently=False)
    except Exception as e:
        print(e)

#  when user click the link in their email this below function will exucte to change verify field from 0 to 1
def verify(request, auth_token):
    try:
        profile_obj = Profile.objects.filter(auth_token=auth_token).first()
        if profile_obj:
            profile_obj.is_verified = True
            profile_obj.save()
            messages.success(request, 'Your account has been verified.')
            return redirect('success')
        else:
            return redirect('error')
    except Exception as e:
        print(e)


def error(request):
    return render(request, 'error.html')