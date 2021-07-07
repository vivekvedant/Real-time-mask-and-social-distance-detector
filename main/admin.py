from django.contrib import admin
from main.models import Customer,Telegram_users,CCTV
# Register your models here.
admin.site.register(Customer)
admin.site.register(Telegram_users)
admin.site.register(CCTV)