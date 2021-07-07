from django.db import models
import uuid

class Customer(models.Model):
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    PhoneNumber = models.CharField(max_length  = 15)

    def __str__(self): 
        return self.username



class Telegram_users(models.Model):
    login_user = models.CharField(max_length = 100)
    username = models.CharField(max_length = 100)
    group_name = models.CharField(max_length = 100)

    def __str__(self):
        return self.username



class CCTV(models.Model):
    login_user = models.CharField(max_length = 100)
    cctv_name = models.CharField(max_length = 100)
    server_url = models.CharField(max_length = 200)
    mask_detection = models.BooleanField()
    social_distance = models.BooleanField()

    def __str__(self):
        return self.cctv_name


