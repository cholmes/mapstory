from mapstory.models import *
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.admin import UserAdmin

class ResourceForm(forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea)
    class Meta:
        model = Resource
        
class ResourceAdmin(admin.ModelAdmin):
    list_display = 'id','name','order'
    list_display_links = 'id',
    list_editable = 'name','order'
    form = ResourceForm
    ordering = ['order',]

class SectionForm(forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea)
    class Meta:
        model = Section

class SectionAdmin(admin.ModelAdmin):
    list_display = 'id','name','order'
    list_display_links = 'id',
    list_editable = 'name','order'
    form = SectionForm
    ordering = ['order',]
    
class VideoLinkForm(forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea)
    class Meta:
        model = VideoLink

class VideoLinkAdmin(admin.ModelAdmin):
    list_display = 'id','name','title','href','publish','location'
    list_display_links = 'id',
    list_editable = 'name','title','publish','href','location'
    form = VideoLinkForm
    
class ContactDetailAdmin(admin.ModelAdmin):
    pass

#@hack the UserAdmin to enable sorting by date_joined
UserAdmin.list_display += ('date_joined',)

admin.site.register(VideoLink, VideoLinkAdmin)
admin.site.register(Section, SectionAdmin)
admin.site.register(ContactDetail, ContactDetailAdmin)
admin.site.register(Resource, ResourceAdmin)
admin.site.register(Topic)
