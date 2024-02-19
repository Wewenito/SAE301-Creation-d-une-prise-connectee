from django.db import models
from django.core.exceptions import ValidationError
import datetime
from datetime import datetime
from django.utils import timezone


class Donnees(models.Model): 

    date = models.CharField(max_length=255) 
    on_off = models.BooleanField()
    topicname = models.CharField(max_length=255)
    
    def __str__(self):
        chaine = f"{self.date} {self.on_off}"
        return chaine

class Temp(models.Model): 

    temp = models.FloatField(null=True)
    date = models.CharField(max_length=255)
    topicname = models.CharField(max_length=255) 


class Humitide(models.Model): 

    humidite = models.FloatField(null=True)
    date = models.CharField(max_length=255)
    topicname = models.CharField(max_length=255) 


class Pression(models.Model): 

    pression = models.FloatField(null=True)
    date = models.CharField(max_length=255)
    topicname = models.CharField(max_length=255) 
    altitude = models.FloatField(null=True)


class Plageshoraires(models.Model):

    CHOICES = [
    ("PRISE1", "Prise 1"),
    ("PRISE2", "Prise 2"),
    ("PRISE3", "Prise 3")
    ]

    datetime_debut = models.DateTimeField(auto_now=False, auto_now_add=False)
    datetime_fin = models.DateTimeField(auto_now=False, auto_now_add=False)
    plages_on_off = models.BooleanField(default=False, null=True, blank=True)
    topicname = models.CharField(max_length=255, choices=CHOICES) 

    @staticmethod
    def validate_datedebut(datetime_debut):
        if datetime_debut < timezone.now():
            raise ValidationError("La date est dépassée.")

    @staticmethod
    def validate_datefin(datetime_fin):
        if datetime_fin < timezone.now():
            raise ValidationError("La date est dépassée.")

    def clean(self):
        super().clean()
        if self.datetime_debut and self.datetime_fin:
            self.validate_datedebut(self.datetime_debut)
            self.validate_datefin(self.datetime_fin)





# Create your models here.
