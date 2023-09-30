from django.shortcuts import render , redirect
from .forms import *
from django.contrib.auth.models import User
from django.contrib import messages
import re
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from .models import *
from datetime import datetime
from .decorators import *


def home(request):
    return render(request , 'main.html' , {'title':"Home"})


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            if User.objects.filter(username=username).exists():
                messages.error(request , 'This username is already taken. Please choose a different username.')
                return redirect("register")

            if User.objects.filter(email=email).exists():
                messages.error(request , 'This email is already registered. Please use a different email.')
                return redirect('register')
            
            if not password[0].isupper():
                messages.error(request , 'Password must start with a capital letter.')
                return redirect('register')
            
            if len(password) < 8:
                messages.error(request , 'Password must be at least 8 characters long.')
                return redirect('register')

            if not re.search(r'\d', password):
                messages.error(request , 'Password must contain at least one number.')
                return redirect('register')
            

            
            user = User(username=username,email=email)
            user.set_password(password)
            user.save()

            return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field.capitalize()}: {error}')

    else:
        form = UserRegisterForm()
    
    return render(request , 'register.html', {'form':form , 'title':'Register'})

def login(request):
    if request.method == 'POST':
        email_or_username = request.POST.get('emailorusername')  # Use get() to avoid KeyError
        password = request.POST.get('password')

        if not email_or_username:
            messages.error(request, 'Username or email is required.')
            return redirect('login')

        if not password:
            messages.error(request, 'Password is required.')
            return redirect('login')

        user = authenticate(request, username=email_or_username, password=password)

        if user is not None:
            auth_login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid credentials')

    return render(request, 'login.html', {'title': 'Login'})



@login_required(login_url='login')
def select_date_and_time(request):
    dates = Dates.objects.all() 
    if request.method == 'POST':
        date = request.POST.get('date')
        time = request.POST.get('time')

        if not dates:
            messages.info(request, 'Currently, there are no appointments available.', extra_tags='error')
            return redirect('appointment1')
            
        date_datetime = datetime.fromisoformat(date)
        
        request.session['date'] = date_datetime.isoformat()
        request.session['time'] = time
        return redirect('appointment')

    return render(request, 'select_date_time_appointment.html', {'dates': dates , 'title':'Select date and time'})





@login_required(login_url='login')
@date_time_selected_required
def create_appointment(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        date_str = request.session.get('date')
        time = request.session.get('time')
        
        date = datetime.fromisoformat(date_str)

        if Appointment.objects.filter(email=email).exists():
            messages.error(request, 'This email is already booked for an appointment.', extra_tags='error')
            return redirect('appointment')

        if Appointment.objects.filter(phone_number=phone_number).exists():
            messages.error(request, 'This Phone number is already booked for an appointment.', extra_tags='error')
            return redirect('appointment')

        booking = Appointment.objects.create(name=name, email=email, phone_number=phone_number, date=date, time=time, user=request.user)
        booking.save()

        subject = 'Appointment Confirmation'
        message = f'Thank you for the appointment \n\n Dear {booking.name},\n\nYour appointment for {booking.date.date()} at {booking.time} has been successfully booked.\n\nYour token number is: {booking.token} \n\nPhone Number: {booking.phone_number}\n\nIf you want to cancel the appointment, just call: 91XXXXXXXX \n\nThank you!'
        from_email = settings.EMAIL_HOST_USER 
        recipient_list = [booking.email]

        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        del request.session['date']
        del request.session['time']
        messages.success(request, 'Appointment created successfully.', extra_tags='success')    
    return render(request, 'appointment.html' , {'time':'appointment' , 'title':'Appointment'})

@login_required(login_url='login')
def patients(request):
    if not request.user.is_superuser:
        return render(request , 'access_denied.html')
    morningappointments = Appointment.MorningAppointments()
    eveningappointments = Appointment.EveningAppointments()
    return render(request , 'todaypatients.html' , {'morningappointments':morningappointments , 'eveningappointments':eveningappointments ,  'title':'Patient' } )

