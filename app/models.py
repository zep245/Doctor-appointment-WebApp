from django.db import models
from datetime import date
from django.utils import timezone
from django.contrib.auth.hashers import make_password


class Patients(models.Model):
    email = models.EmailField(unique=True , blank=False)
    password = models.CharField(max_length=20)

    class Meta:
        verbose_name_plural = "Patients"

    @classmethod
    def get_Patients_by_email(cls, email):
        try:
            return cls.objects.get(email=email)
        except cls.DoesNotExist:
            return None

    def set_password(self, raw_password):
        self.password = make_password(raw_password)


    def __str__(self):
        return self.email


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
            raise ValueError("Date cannot be in the past.")
        super().save(*args , **kwargs)

    def __str__(self):
        return str(self.date)


class Appointment(models.Model):
    user = models.ForeignKey(Patients, on_delete=models.CASCADE, default=None)
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



