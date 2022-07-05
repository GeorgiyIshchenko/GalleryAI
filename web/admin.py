from django.contrib import admin
from django import forms

from .models import *

admin.site.register(CustomUser)
admin.site.register(Photo)
admin.site.register(Tag)
