from django.db import models
from django import forms

from mapstory.models import ContactDetail

class ProfileForm(forms.ModelForm):
    
    blurb = forms.CharField(widget=forms.Textarea)
    biography = forms.CharField(widget=forms.Textarea)
    education = forms.CharField(widget=forms.Textarea)
    expertise = forms.CharField(widget=forms.Textarea)
    
    class Meta:
        model = ContactDetail
        exclude = ('user','fax','delivery','zipcode','area','links')