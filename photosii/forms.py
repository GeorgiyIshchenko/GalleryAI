from django import forms

from .models import *


class DataSetCreationForm(forms.Form):
    GEEKS_CHOICES = (
        ("1", "One"),
        ("2", "Two"),
        ("3", "Three"),
        ("4", "Four"),
        ("5", "Five"),
    )
    tag = forms.ChoiceField(choices=GEEKS_CHOICES)
