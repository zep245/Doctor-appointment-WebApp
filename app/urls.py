from django.urls import path
from . import views

urlpatterns = [
    path('' , views.home , name='home'),
    path('register/' , views.register , name='register'),
    path('login/' , views.login , name='login'),
    path('select_date_time/' , views.select_date_and_time , name='appointment1'),
    path('appointment/' , views.create_appointment , name='appointment'),
    path('patients/today/' , views.patients , name='today_patients'),
]