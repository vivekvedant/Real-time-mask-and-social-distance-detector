from django.contrib import admin
from django.urls import path,include,re_path
from main import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.login,name = 'login'),
    # path('login/',views.login,name = 'login'),
    path('users/',views.users,name = 'users'),
    path('cctv_view/',views.cctv_view,name = 'cctv_view'),
    path('display_all_camera/',views.display_all_camera,name = 'display_all_camera'),
    re_path(r'mask_feed/(?P<mask_camera_ip>(.*?))/$' ,views.mask_feed,name = "mask_feed"),
    re_path(r'predistraion_feed/(?P<predistraion_camera_ip>(.*?))/$' ,views.predistraion_feed,name = "predistraion_feed"),
    re_path(r'delete_cctv/(?P<cctv_name>(.*?))/$' ,views.delete_cctv,name = "delete_cctv"),
    re_path(r'edit_cctv/(?P<cctv_name>(.*?))/$' ,views.edit_cctv,name = "edit_cctv"),
    # re_path(r'/send_image/(?P<username>(.*?))/$' ,views.send_image,name = "send_image"),
    path('login/',views.login,name = 'login'),
    path('forgot_password/',views.forgot_password,name = 'forgot_password'),
    path('verify_otp/',views.verify_otp,name = 'verify_otp'),
    path('confirm_password/',views.confirm_password,name = 'confirm_password'),
    path('registration/',views.registration,name = 'registration'),
    path('verification/',views.verification,name = 'verification'),
    path('add_users/',views.add_users,name = 'add_users'),
    path('add_cctv/',views.add_cctv,name = 'add_cctv'),
    re_path(r'edit_user/(?P<username>(.*?))/$' ,views.edit_user,name = "edit_user"),
    path('delete_user/<str:username>/<str:group_name>', views.delete_user,name = 'delete_user'),
    path('logout/',views.logout,name = 'logout')
    
]
