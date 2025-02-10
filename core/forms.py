from logging import PlaceHolder
from random import choices
from django import forms
from core.models import (User,Patient,Report)
import decimal

d = decimal.Decimal
    
class PatientForm(forms.ModelForm):
    created_by = forms.CharField(max_length=100, required=False)
    class Meta:
        model = Patient
        fields = ["first_name", "last_name", "date_of_birth","national_id","medcare",
                  "patient_id", "gender","blood_type", "occupation", "country", 
                  "county", "subcounty", "city","area", "mobile", "pincode","email"]

    def __init__(self, *args, **kwargs):
        #self.user = kwargs.pop("user", None)
        #self.patient = kwargs.pop('patient', None)
        super(PatientForm, self).__init__(*args, **kwargs)
        not_required = ['county', 'subcounty','city', 
                        'area', 'mobile','pincode', 'last_name']
        for field in not_required:
            self.fields[field].required = False

    def clean_mobile(self):
        phone_number = self.cleaned_data.get('mobile')
        try:
            if int(phone_number):
                check_phone = str(phone_number)
                if not phone_number or not(len(check_phone) == 10):
                    raise forms.ValidationError(
                        'Please enter a valid 10 digit phone number')
                return phone_number
        except ValueError:
            raise forms.ValidationError('Please enter a valid phone number')

    def clean_pincode(self):
        pincode = self.cleaned_data.get('pincode')
        if pincode:
            try:
                if int(pincode):
                    check_pin = str(pincode)
                    if not len(check_pin) == 6:
                        raise forms.ValidationError(
                            'Please enter a valid 6 digit pincode')
            except ValueError:
                raise forms.ValidationError(
                    'Please enter a valid pincode')
        return pincode

'''     def save(self, commit=True, *args, **kwargs):
        instance = super(PatientForm, self).save(commit=False, *args, **kwargs)
        instance.created_by = User.objects.filter(
           username=self.cleaned_data.get('created_by')).first()
        if commit:
            instance.save()
        return instance  '''
   
class UpdatePatientProfileForm(forms.ModelForm):
    #photo = forms.FileField()
    #signature = forms.FileField()
    class Meta:
        model = Patient
        fields = ["photo"]
    #def __init__(self, instance, *args, **kwargs):
     #   super(UpdatepatientProfileForm, self).__init__(*args, **kwargs)
        
class UserForm(forms.ModelForm):
    
    #date_of_birth = forms.DateField(
     #   required=False,
     #   input_formats=['%m/%d/%Y'])
    password = forms.CharField(max_length=100, required=False)

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name",
                  "user_roles", "username", "county","date_of_birth",
                  "subcounty", "city", "area", "mobile", "pincode"]

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)

        #self.fields['gender'].widget.attrs.update({
         #       'placeholder': 'Gender',
         # #'class': 'text-box wid-form select-box-pad'})
        not_required_fields = [ 'county', 'subcounty',
                               'city', 'area', 'mobile',
                               'pincode', 'last_name']
        for field in not_required_fields:
            self.fields[field].required = False
        if not self.instance.pk:
            self.fields['password'].required = True

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            if len(password) < 5:
                raise forms.ValidationError(
                    'Password must be at least 5 characters long!')
        return password

    def clean_pincode(self):
        pincode = self.cleaned_data.get('pincode')
        if pincode:
            try:
                if int(pincode):
                    check_pin = str(pincode)
                    if not len(check_pin) == 6:
                        raise forms.ValidationError(
                            'Please enter a valid 6 digit pincode')
            except ValueError:
                raise forms.ValidationError(
                    'Please enter a valid pincode')
        return pincode

    def clean_mobile(self):
        phone_number = self.cleaned_data.get('mobile')
        try:
            if phone_number is not None:
                if int(phone_number):
                    check_phone = str(phone_number)
                    if not phone_number or not(len(check_phone) == 10):
                        raise forms.ValidationError(
                            'Please enter a valid 10 digit phone number')
                    return phone_number
        except ValueError:
            raise forms.ValidationError('Please enter a valid phone number')

    def save(self, commit=True, *args, **kwargs):
        instance = super(UserForm, self).save(commit=False, *args, **kwargs)
        if not instance.id:
            instance.pincode = self.cleaned_data.get('pincode')
            instance.set_password(self.cleaned_data.get('password'))
        if commit:
            instance.save()
        return instance
class ReportForm(forms.ModelForm):
    
    class Meta:
        model = Report
        fields = ["first_name", "last_name","doc_id", "patient",
                  "blood_type","medcare","city", "pincode",
                  "staff", "diagnosis","medical_history"]
class MyForm(forms.Form):
    template_name = "report/viewreport.html"       


class ChangePasswordForm(forms.Form):
    
    current_password = forms.CharField(max_length=50, required=True)
    new_password = forms.CharField(max_length=50, required=True)
    confirm_new_password = forms.CharField(max_length=50, required=True)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super(ChangePasswordForm, self).__init__(*args, **kwargs)

    def clean_current_password(self):
        current = self.cleaned_data.get("current_password")
        if not self.user.check_password(current):
            raise forms.ValidationError("Current Password is Invalid")
        return current

    def clean_new_password(self):
        password = self.cleaned_data.get("new_password")
        if len(password) < 5:
            raise forms.ValidationError("Password must be at least 5 characters")
        return password

    def clean_confirm_new_password(self):
        password = self.cleaned_data.get("new_password")
        confirm = self.cleaned_data.get("confirm_new_password")
        if password != confirm:
            raise forms.ValidationError("Passwords does not match")
        return confirm

