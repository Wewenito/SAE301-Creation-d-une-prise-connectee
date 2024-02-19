from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _
from . import models
from django import forms

class DonneesForm(ModelForm):
    class Meta:
        model = models.Donnees
        fields = ('date', 'on_off', 'topicname')
        labels = {
            'date' : _('Date ') ,
            'on_off' : _('On ou Off'),
            'topicname' : _('Topicname ')
    }
        


class TempForm(ModelForm):
    class Meta:
        model = models.Temp
        fields = ('temp', 'date', 'topicname')
        labels = {
            'temp' : _('Température '),
            'date' : _('Date '),
            'topicname' : _('Topicname ')
    }
        


class HumiditeForm(ModelForm):
    class Meta:
        model = models.Humitide
        fields = ('humidite', 'date', 'topicname')
        labels = {
            'humidite' : _('Humidité '),
            'date' : _('Date '),
            'topicname' : _('Topicname ')
    }


class PressionForm(ModelForm):
    class Meta:
        model = models.Pression
        fields = ('pression', 'date', 'topicname', "altitude")
        labels = {
            'pression' : _('Pression '),
            'date' : _('Date '),
            'topicname' : _('Topicname '),
            'altitude' : _('Altitude ')
    }
     
class PlageshorairesForm(ModelForm):
    datetime_debut = forms.DateTimeField(
        label=_('Date de début '),
        widget=forms.DateTimeInput(attrs={'class':"form-control", 'type': 'datetime-local'}),
    )
    datetime_fin = forms.DateTimeField(
        label=_('Date de fin '),
        widget=forms.DateTimeInput(attrs={'class':"form-control", 'type': 'datetime-local'})
    )

    plages_on_off = forms.BooleanField(
        required=False,
        label=_('On ou Off '),
        widget=forms.CheckboxInput(attrs={'class':"form-check-input"})
    )

    topicname = forms.CharField(
        label=_('topicname '),
        widget=forms.Select(attrs={'class': 'custom-select'},choices=[('', 'Choisir...')] + models.Plageshoraires.CHOICES))

    class Meta:
        model = models.Plageshoraires
        fields = ('datetime_debut', 'datetime_fin', 'plages_on_off', "topicname")
        labels = {
            'datetime_debut' : _('Date de début '),
            'datetime_fin' : _('Date de fin '),
            'plages_on_off' : _('On ou Off '),
            'topicname' : _('topicname ')
    }
