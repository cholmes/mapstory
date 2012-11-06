from django import forms
from account.forms import SignupForm
from geonode.maps.models import Layer
from mapstory.models import ContactDetail
import taggit


class LayerForm(forms.ModelForm):
    '''we have metadata needs/desires different from what geonode gives'''
    
    keywords = taggit.forms.TagField(required=False)
    abstract = forms.CharField(required=False)
    purpose = forms.CharField(required=False)
    supplemental_information = forms.CharField(required=False)
    data_quality_statement = forms.CharField(required=False)

    class Meta:
        model = Layer
        exclude = ('contacts','workspace', 'store', 'name', 'uuid', 'storeType', 'typename') + \
        ('temporal_extent_start', 'temporal_extent_end', 'topic_category') + \
        ('keywords_region','geographic_bounding_box','constraints_use','date','date_type')


class StyleUploadForm(forms.Form):
    
    layerid = forms.IntegerField()
    name = forms.CharField(required=False)
    update = forms.BooleanField(required=False)
    sld = forms.FileField()
    


class ProfileForm(forms.ModelForm):
    
    blurb = forms.CharField(widget=forms.Textarea)
    biography = forms.CharField(widget=forms.Textarea)
    education = forms.CharField(widget=forms.Textarea)
    expertise = forms.CharField(widget=forms.Textarea)
    
    class Meta:
        model = ContactDetail
        exclude = ('user','fax','delivery','zipcode','area','links')
        

class CheckRegistrationForm(SignupForm):
    '''add a honey pot field and verification of a hidden client generated field'''
    
    not_human = forms.BooleanField(
                widget=forms.HiddenInput,
                required = False)

    def clean(self):
        if not self.data.get('human',None):
            raise forms.ValidationError('If you are human, ensure you say so.')
        return self.cleaned_data

    def clean_not_human(self):
        if self.cleaned_data['not_human']:
            raise forms.ValidationError('')
