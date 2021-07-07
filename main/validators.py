from main.models import Customer,CCTV
from django.core.exceptions import ValidationError
import hashlib
import re
import cv2

class ValidationRules:

    def authenticate(self,username,password):
        try:
            Customer_password = Customer.objects.get(username = username)
            salt, _ = Customer_password.password.split('_')
            hashed_password = hashlib.sha1(salt.encode() + password.encode()).hexdigest()
            seprator = b'_'
            latest_password =salt.encode() + seprator + hashed_password.encode()
            Customer_username = Customer.objects.filter(username = username,password  = latest_password.decode("utf-8"))
        except Customer.DoesNotExist:
            Customer_username = None   
    
    
        if not Customer_username:
             raise ValidationError('Username Doesn\'t exist')
        
    def check_user(self,username,phonenumber):
        try:
            Customer_detail = Customer.objects.filter(username = username,PhoneNumber = phonenumber)
        except Customer.DoesNotExist:
            Customer_detail = None
        if not Customer_detail:
            raise ValidationError('Username Doesn\'t exist')
    
    def validate_name(self,username):
        if not username:
            raise ValidationError('Username is required')
   
    def validate_password(self,password):
       if not password:
           raise ValidationError('Password is required')
    
    def validate_phone(self,phone):
        if not phone:
            raise ValidationError("Phone is required")
    

    def Already_exist(self,username):
        username = Customer.objects.filter(username = username)
        if username :
             raise ValidationError('Username already exist')
        
    
    def validate_otp(self,otp):
        if not otp:
            raise ValidationError("Code is required")
    
    def cctv_name_required(self,cctv_name):
        if not cctv_name:
            raise ValidationError('Cctv Name is required')

    def cctv_name_exist(self,cctv_name):
        cctv_name = CCTV.objects.filter(cctv_name = cctv_name)
        if cctv_name:
            raise ValidationError('CCTV name already exist ')
        
    def server_url_required(self,url):
        if not url:
            raise ValidationError('Server Url is Required')

    def validate_detection_option(self,mask_detection,social_distance):
        if   social_distance == 'off' and   mask_detection == 'off':
            raise ValidationError('One of the option should be selected')
        
    def check_urls(self,video_url):
        cap = cv2.VideoCapture(video_url)
        if cap is None or not cap.isOpened():
            raise ValidationError("Url is not valid")
        