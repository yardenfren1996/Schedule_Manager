from django import forms
from django.contrib.auth.models import User
from .models import WorkerProfileInfo, Shift


class WorkerForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password')


class WorkerProfileInfoForm(forms.ModelForm):
    class Meta:
        model = WorkerProfileInfo
        fields = ('worker_number', 'city_address', 'gate_worker')

# class ShiftsDictForm(forms.ModelForm):
#     class Meta:
#         model =

#
# class ShiftSubmissionForm(forms.ModelForm):
#     class Meta:
#         model = WorkerProfileInfo
# class ShiftSelectionForm(forms.ModelForm):
#     class Meta:
#         fields = ('dates')
