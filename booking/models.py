from django.db import models

# Create your models here.

class Users(models.Model):
    name=models.CharField(max_length=200)
    email=models.CharField(max_length=200)
    password=models.CharField(max_length=200)
    role=models.CharField(max_length=200)

class Events(models.Model):
        title = models.CharField(max_length=200)
        location = models.CharField(max_length=200)
        date = models.CharField(max_length=200)
        total_seats =  models.PositiveIntegerField()
        available_seats= models.PositiveIntegerField()


class Bookings(models.Model):
    seats_booked = models.PositiveIntegerField()
    status = models.CharField(max_length=200)

