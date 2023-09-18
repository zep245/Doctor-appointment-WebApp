from django.db import models
from datetime import date
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError




class Dates(models.Model):
    date = models.DateField()

    class Meta:
        verbose_name_plural = "Date"

    def delete(self, *args, **kwargs):
        delete_dates = self.dates
        if delete_dates < timezone.now().date():
            self.delete()
        return delete_dates


    def save(self,*args , **kwargs):
        if self.date < timezone.now().date():
            raise ValidationError('You cannot add past dates')
        super().save(*args , **kwargs)

    def __str__(self):
        return str(self.date)


class Appointment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    name = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=10, default=None , unique=True)
    date = models.DateField()
    time = models.TextField()
    token = models.PositiveIntegerField()

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.pk:  # Generate token only for new instances
            # Filter appointments based on the selected time
            appointments_at_same_time = Appointment.objects.filter(time=self.time)
            if appointments_at_same_time.exists():
                last_appointment = appointments_at_same_time.order_by('-token').first()
                token = last_appointment.token + 1
            else:
                token = 1
            self.token = token
        super().save(*args, **kwargs)

    def delete(self):
        if self.date < timezone.now.date():
            self.delete()

    @classmethod
    def MorningAppointments(cls):
        return cls.objects.filter(date=date.today(), time='10:00 AM')

    @classmethod
    def EveningAppointments(cls):
        return cls.objects.filter(date=date.today(), time='4:00 PM')
