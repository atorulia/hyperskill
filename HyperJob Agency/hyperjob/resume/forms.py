from django import forms


class CreateResumeForm(forms.Form):
    description = forms.CharField(label="Description")
