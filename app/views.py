from django.shortcuts import render , redirect
from .forms import *
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import *
from datetime import datetime
from .decorators import *
from django.views import View
from django.contrib.auth.hashers import make_password , check_password
from .utils import password_reset_token_generator
from django.urls import reverse
from .login_required import patient_login_required
from django.contrib.auth.decorators import login_required

def home(request):
    return render(request , 'main.html' , {'title':"Home"})



class Signup(View):
    def get(self , request):
        return render(request , 'register.html' , {'title':'Register'})


    def post(self , request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get("password2")


        if len(password and password2) < 8:
            messages.error(request , 'Password must be at least 8 characters long.')
            return redirect("register")

        if password != password2:
            messages.error(request , "Password not match try again.")
            return redirect('register')
        
        if Patients.objects.filter(email=email).exists():
            messages.error(request , 'This email is already registered. Please use a different email.')
            return redirect('register')
        
        if not password[0].isupper():
            messages.error(request , 'Password must start with a capital letter.')
            return redirect('register')
            
        Patients.objects.create(email=email , password = make_password(password))
        return redirect('login')



def passwordReset(request):
    if request.method == 'POST':
        email = request.POST.get('password_reset_email')
        user = Patients.objects.filter(email=email).first()
        if user:
            token = password_reset_token_generator.generate_token(user)
            reset_link = settings.BASE_URL + reverse('password_change' , kwargs={'token':token})
        
            # send by email
            subject = 'Password Reset'
            message = f'Please click the following link to reset your password:\n{reset_link}'
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [user.email]

            send_mail(subject, message, from_email, recipient_list, fail_silently=False)
            messages.success(request , "Password reset link sent to your email.")
            return redirect("password_reset")
        else:
            messages.error(request, 'No user found with that email.')
    return render(request , "password_reset.html" , {'title':'Password reset'})


def passwordChange(request, token):
    try:
        user_id = password_reset_token_generator.validate_token(token)
        if user_id:
            user = Patients.objects.filter(id=user_id).first()
            if user:
                if request.method == "POST":
                    new_password = request.POST.get('new_password')
                    retype_password = request.POST.get('retype_password')
                    if new_password == retype_password:
                        user.set_password(new_password)
                        user.save()
                        messages.success(request, 'Password changed successfully. You can now log in with your new password.')
                        return redirect("login")
                    else:
                        messages.error(request, "Passwords do not match.")
                return render(request, 'password_change.html', {'token': token})
            else:
                messages.error(request, "No user found!")
                return redirect("password_reset")
        return redirect("password_reset" , {'title':'Password change'})
    except:
        messages.error(request , "This link is expire please re generate")
        return redirect("password_reset")

# def register(request):
#     if request.method == 'POST':
#         form = UserRegisterForm(request.POST)
#         if form.is_valid():
#             username = form.cleaned_data['username']
#             email = form.cleaned_data['email']
#             password = form.cleaned_data['password']

#             if User.objects.filter(username=username).exists():
#                 messages.error(request , 'This username is already taken. Please choose a different username.')
#                 return redirect("register")

#             if User.objects.filter(email=email).exists():
#                 messages.error(request , 'This email is already registered. Please use a different email.')
#                 return redirect('register')
            
#             if not password[0].isupper():
#                 messages.error(request , 'Password must start with a capital letter.')
#                 return redirect('register')
            
#             if len(password) < 8:
#                 messages.error(request , 'Password must be at least 8 characters long.')
#                 return redirect('register')

#             if not re.search(r'\d', password):
#                 messages.error(request , 'Password must contain at least one number.')
#                 return redirect('register')
            

            
#             user = User(username=username,email=email)
#             user.set_password(password)
#             user.save()

#             return redirect('login')
#         else:
#             for field, errors in form.errors.items():
#                 for error in errors:
#                     messages.error(request, f'{field.capitalize()}: {error}')

#     else:
#         form = UserRegisterForm()
    
#     return render(request , 'register.html', {'form':form , 'title':'Register'})

class Login(View):

    def get(self , request):
        return render(request , 'login.html' , {'title':'Login'})
    
    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        patients = Patients.get_Patients_by_email(email)

        if patients:
            if check_password(password, patients.password):
                request.session['patient'] = patients.id
                return redirect('home') 
            else:
                messages.error(request, 'Invalid password')
        else:
            messages.error(request, 'Patient not found')

        return render(request, 'login.html', {'customers': patients})



class Logout(View):
    def get(self, request):
        # Use pop to remove the 'customer' key from the session
        request.session.pop('patient', None)
        return redirect('login')


# def login(request):
#     if request.method == 'POST':
#         email_or_username = request.POST.get('emailorusername')  # Use get() to avoid KeyError
#         password = request.POST.get('password')

#         if not email_or_username:
#             messages.error(request, 'Username or email is required.')
#             return redirect('login')

#         if not password:
#             messages.error(request, 'Password is required.')
#             return redirect('login')

#         user = authenticate(request, username=email_or_username, password=password)

#         if user is not None:
#             auth_login(request, user)
#             return redirect('home')
#         else:
#             messages.error(request, 'Invalid credentials')

#     return render(request, 'login.html', {'title': 'Login'})



@patient_login_required(login_url='login')
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





@patient_login_required(login_url='login')
@date_time_selected_required
def create_appointment(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        date_str = request.session.get('date')
        time = request.session.get('time')

        patient_id = request.session['patient']
        patient = Patients.objects.get(id=patient_id)
        
        date = datetime.fromisoformat(date_str)

        if Appointment.objects.filter(email=email).exists():
            messages.error(request, 'This email is already booked for an appointment.', extra_tags='error')
            return redirect('appointment')

        if Appointment.objects.filter(phone_number=phone_number).exists():
            messages.error(request, 'This Phone number is already booked for an appointment.', extra_tags='error')
            return redirect('appointment')

        booking = Appointment.objects.create(name=name, email=email, phone_number=phone_number, date=date, time=time, user=patient)
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
