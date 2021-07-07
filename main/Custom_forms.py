from django import forms
from main.models import Customer ,Telegram_users, CCTV
from django.forms.utils import ErrorList
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe


my_default_errors = {
    'required': 'This field is required',
    'invalid': 'Enter a valid value'
}

class DivErrorList(ErrorList):
    def __str__(self):
        return self.as_divs()
    def as_divs(self):
        if not self: return ''
        return mark_safe('<div class="errors">%s</div>' % ''.join(['<div class="error">%s</div>' % e for e in self]))


class Login(forms.Form):
    username = forms.CharField(label = "username", max_length=100,required=False,error_messages=my_default_errors)
    password = forms.CharField(label = "password",  max_length=100,required=False,error_messages=my_default_errors)

    def clean_username(self):
        cleaned_data = super(Login,self).clean()
        username = cleaned_data.get('username')
        if not username:
            self.add_error('username','Username is required')
          
        return username

    def clean_password(self):
        cleaned_data = super(Login,self).clean()
        password = cleaned_data.get('password')
        if not password:
            self.add_error('password','Password is required')
         
        return password
    
class Forgot_password(forms.Form):
    username = forms.CharField(label = "username", max_length=100,required=False,error_messages=my_default_errors)
    phonenumber = forms.CharField(label = "phonenumber",  max_length=100,required=False,error_messages=my_default_errors)

    def clean_username(self):
        cleaned_data = super(Forgot_password,self).clean()
        username = cleaned_data.get('username')
        if not username:
            self.add_error('username','Username is required')
          
        return username

    def clean_phonenumber(self):
        cleaned_data = super(Forgot_password,self).clean()
        phonenumber = cleaned_data.get('phonenumber')
        if not phonenumber:
            self.add_error('phonenumber','phonenumber is required')
         
        return phonenumber
    
class OTP(forms.Form):
    otp_code = forms.CharField(label = 'otp_code',max_length=100,required=False,error_messages=my_default_errors)

    def clean_otp(self):
        cleaned_data = super(OTP,self).clean()
        otp_code = cleaned_data.get('otp_code')
        if not otp_code:
            self.add_error('otp_code','otp is required')
        return otp_code

class New_password(forms.Form):
    new_password = forms.CharField(label = 'new_password',max_length=100,required = False,error_messages=my_default_errors)
    confirm_password = forms.CharField(label = 'confirm_password',max_length=100,required = False,error_messages=my_default_errors)

    def clean_new_password(self):
        clean_data_new_password = super(New_password,self).clean()
        new_password = clean_data_new_password.get('new_password')
        if not new_password:
            self.add_error('new_password','New Password is required')

        return new_password

    def clean_confirm_password(self):
        clean_data_confirm_password = super(New_password,self).clean()
        confirm_password = clean_data_confirm_password.get('confirm_password')
        if not confirm_password:
            self.add_error('confirm_password','Confirm Password is required')
            
        return confirm_password

    


class Registration(forms.ModelForm):
    class Meta:
        model = Customer
        fields =['username','password','PhoneNumber']
        


class Telegram_users_form(forms.ModelForm):
    class Meta:
        model = Telegram_users
        fields = ['login_user','username','group_name']



class Cttv_forms(forms.ModelForm):
    class Meta:
        model = CCTV
        fields = ['login_user','cctv_name','server_url','mask_detection','social_distance']