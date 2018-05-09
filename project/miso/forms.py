from django import forms
from django.forms import ModelForm
from .models import *


class StaffForm(ModelForm):
    class Meta:
        model = Staff
        fields = ['name', 'phone', 'score', 'possible_N_days']

