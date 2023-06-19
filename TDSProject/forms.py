from django import forms
from TDSProject.models import Q

class Qforms(forms.ModelForm):
    
    class Meta:
        model=Q
        fields="__all__"


