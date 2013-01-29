from django import forms
from account.forms import SignupForm
from geonode.maps.models import Layer
from mapstory.models import ContactDetail
import taggit


class LayerForm(forms.ModelForm):
    '''we have metadata needs/desires different from what geonode gives.
    ignore a bunch of stuff and make sure others are optional
    '''
    
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
    '''Override the default with our requirements:
    hide some fields, make some required, others not
    allow saving some user fields here'''

    first_name = forms.CharField()
    last_name = forms.CharField()
    blurb = forms.CharField(widget=forms.Textarea)
    biography = forms.CharField(widget=forms.Textarea, required=False)
    education = forms.CharField(widget=forms.Textarea, required=False)
    expertise = forms.CharField(widget=forms.Textarea, required=False)

    def __init__(self, *args, **kw):
        super(ProfileForm, self).__init__(*args, **kw)
        # change the order they appear in
        order = ('first_name', 'last_name', 'blurb')
        fields = self.fields
        self.fields = type(fields)()
        for o in order:
            self.fields[o] = fields[o]
        self.fields.update(fields)
        user = self.instance.user
        self.initial['first_name'] = user.first_name
        self.initial['last_name'] = user.last_name

    def save(self, *args, **kw):
        super(ProfileForm, self).save(*args, **kw)
        data = self.cleaned_data
        user = self.instance.user
        user.first_name = data['first_name']
        user.last_name = data['last_name']
        user.save(*args, **kw)
        self.instance.update_audit()

    class Meta:
        model = ContactDetail
        exclude = ('user','fax','delivery','zipcode','area','links','name')
        

class CheckRegistrationForm(SignupForm):
    '''add a honey pot field and verification of a hidden client generated field'''
    
    not_human = forms.BooleanField(
                widget=forms.HiddenInput,
                required = False)

    def clean(self):
        if not self.data.get('tos',None):
            raise forms.ValidationError('You must agree to the Terms of Service.')
        return self.cleaned_data

    def clean_not_human(self):
        if self.cleaned_data['not_human']:
            raise forms.ValidationError('')
