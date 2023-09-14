from django import forms
from django.contrib.auth.models import User
import re
from .models import *

class UserRegisterForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)


    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already taken. Please choose a different username.')
        return username


    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered. Please use a different email.')
        return email
    
    def clean_password(self):
        password = self.cleaned_data['password']
        if len(password) < 8:
            raise forms.ValidationError('Password must be at least 8 characters long.')
        
        if not password[0].isupper():
            raise forms.ValidationError('Password must start with a capital letter.')
        
        if not re.search(r'\d', password):
            raise forms.ValidationError('Password must contain at least one number.')
        
        return password
        
