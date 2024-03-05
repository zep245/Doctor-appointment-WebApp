from django.urls import path
from . import views

urlpatterns = [
    path('' , views.home , name='home'),
    path('register/' , views.Signup.as_view() , name='register'),
    path('login/' , views.Login.as_view() , name='login'),
    path('logout/' , views.Logout.as_view()  , name='logout'),
    path('select_date_time/' , views.select_date_and_time , name='appointment1'),
    path('appointment/' , views.create_appointment , name='appointment'),
    path('patients/today/' , views.patients , name='today_patients'),
    path('password_reset/' , views.passwordReset  , name='password_reset'),
    path('password_change/<str:token>/' , views.passwordChange  , name='password_change'),
]