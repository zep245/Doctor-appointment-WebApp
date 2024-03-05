from django.contrib import admin
from django.utils import timezone
from .models import *

class PatientTable(admin.ModelAdmin):
    list_display = ['name' , "email" , "phone_number" , 'date' ,'time', 'token']





admin.site.register(Appointment , PatientTable)
admin.site.register(Dates)
