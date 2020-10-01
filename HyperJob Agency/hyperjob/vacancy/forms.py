from django import forms


class CreateVacancyForm(forms.Form):
    description = forms.CharField(label="Description")
