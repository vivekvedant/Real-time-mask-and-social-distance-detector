from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse,StreamingHttpResponse, HttpResponseServerError,HttpResponseRedirect
from django.template import loader
from main.camera import  LiveWebCam
from main.Custom_forms import Login, Forgot_password,OTP,New_password, Registration, DivErrorList,Telegram_users_form,Cttv_forms
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from main.validators import ValidationRules
from main.models import Customer, Telegram_users
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from main.telegram import Messanger
from main.models import Customer,CCTV
from main.image_sender import send_image,run_continuously,run_mask_detector,run_social_detector
import time
import schedule
import bcrypt
import hashlib

# Create your views here.


def login(request):
	loginform = Login(request.POST or None,error_class=DivErrorList)
	telegram_user_form  = Telegram_users(request.POST or None)
	error_list = {}
	error_list['Not_Exist']= ''
	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']
		if loginform.is_valid():

			validator = ValidationRules()
			try:
				validator.authenticate(username = username,password = password)

			except ValidationError:
					error_list['Not_Exist'] = "User Doesn\'t Exist"

			if not  error_list['Not_Exist']:
				context = {
					'telegram_user_form':telegram_user_form
				}
				request.session['username'] = username
				request.session['login']  = True
				return redirect('users')

	context = {
		'loginform':loginform,
		'username_exist':error_list['Not_Exist']
	}
	return render(request,'login.html',context)

def logout(request):
	if 'login' in request.session:
		del request.session['login']
	if 'registration' in request.session:
		del request.session['registration']

	return redirect('/')

def forgot_password(request):
	forgot_password_form = Forgot_password(request.POST or None,error_class=DivErrorList)
	error_list = {}
	error_list['Not_exist'] = ''
	if request.method == 'POST':
		username = request.POST['username']
		request.session['get_username_otp'] = username
		phonenumber = request.POST['phonenumber']
		request.session['get_phone_otp'] = phonenumber
		if forgot_password_form.is_valid():
			validator = ValidationRules()
			try:
				validator.check_user(username,phonenumber)
			except ValidationError:
				error_list['Not_exist'] = "User don't exist"

			if not error_list['Not_exist']:
				return redirect('verify_otp')

	context = {
		'forgot_password_form':forgot_password_form,
		'user_dont_exist':error_list['Not_exist']
	}
	return render(request,'forgot_password.html',context)

def verify_otp(request):
	otp_form = OTP(request.POST or None, error_class = DivErrorList)
	error_list = {}
	error_list['wrong_code'] = ''
	telegram_obj = Messanger(request.session['get_phone_otp'])
	tele_client = telegram_obj.get_client()
	phone_hashed = telegram_obj.get_otp(tele_client)
	if request.method == 'POST':
		if otp_form.is_valid():
			code = request.POST['otp']
			try:
				telegram_obj.get_verified(tele_client,int(code),phone_hashed)
				pass
			except:
				error_list['wrong_code']= 'Code is invalid '

			if not error_list['wrong_code']:
				return redirect('/confirm_password/')
	context = {
		'otp_form':otp_form,
		'wrong_code':error_list['wrong_code']
	}
	return render(request,'Verify_otp.html',context)

def confirm_password(request):
	new_password_form = New_password(request.POST or None, error_class = DivErrorList)
	error_list = {}
	error_list['password_not_same'] = ''
	if request.method == "POST":
		new_password = request.POST['new_password']
		confirm_password = request.POST['confirm_password']
		if new_password != confirm_password:
			error_list['password_not_same'] = "Password doesn\'t match"
		else:
			Customer_detail = Customer.objects.get(username = request.session['get_username_otp'],PhoneNumber = request.session['get_phone_otp'])
			salt = bcrypt.gensalt()
			hashed_password = hashlib.sha1(salt + confirm_password.encode()).hexdigest()
			seprator = b'_'
			final_password = salt + seprator + hashed_password.encode()
			Customer_detail.password = final_password.decode("utf-8")
			Customer_detail.save()
			return redirect('/login/')

	context = {
		'new_password_form':new_password_form,
		'password_not_same':error_list['password_not_same']
	}
	return render(request,'change_password.html',context)

def registration(request):
	registrationform = Registration(request.POST or None,error_class=DivErrorList,use_required_attribute = False)
	error_list = {}
	validator = ValidationRules()
	error_list['username'] = ''
	error_list['password'] = ''
	error_list['username_exist'] = ''
	error_list['phone'] = ''
	error_list['Wrong_phone'] = ''
	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']

		phone = request.POST['PhoneNumber']
		request.session['phone'] = phone


		try:

			validator.validate_name(username = username)

		except ValidationError:
			error_list['username'] = 'Username is required'
		try:
			validator.Already_exist(username = username)
		except  ValidationError:
			error_list['username_exist'] = 'Username already exist'
		try:

			validator.validate_password(password = password)
		except ValidationError:
			error_list['password'] = 'Password is required'
		try:
			validator.validate_phone(phone = phone)
		except ValidationError:
			error_list['phone'] = 'Phone is required'

		if not error_list['username'] and not error_list['username_exist'] and not error_list['password'] and not error_list['phone']:
			telegram_obj = Messanger(phone)

			tele_client = telegram_obj.get_client()
			request.session['phone_hash_code'] = telegram_obj.get_otp(tele_client)
			request.session['username'] = username
			request.session['password'] = password
			tele_client.disconnect()
			return render(request,'verification.html')


	context = {
		'registrationform':registrationform,
		'username_validation':error_list['username'],
		'password_validation':error_list['password'],
		'phone_validation':error_list['phone'],
		'username_exist':error_list['username_exist'],
		'Wrong_phone':error_list['Wrong_phone']
	}
	return render(request,'registration.html',context)


def verification(request):
	salt = bcrypt.gensalt()
	hashed_password = hashlib.sha1(salt + request.session['password'].encode()).hexdigest()
	seprator = b'_'
	request.POST._mutable = True
	request.POST['username'] = request.session['username']
	final_password = salt + seprator + hashed_password.encode()
	request.POST['password']  = final_password.decode("utf-8")
	request.POST['PhoneNumber'] = request.session['phone']
	request.POST._mutable = False
	registrationform = Registration(request.POST or None,error_class=DivErrorList,use_required_attribute = False)
	error_list = {}

	validator = ValidationRules()
	error_list['wrong_code'] = ''
	error_list['Code_required'] = ''

	if request.method == 'POST':
		code = request.POST['code']
		telegram_obj = Messanger(request.session['phone'])

		client = telegram_obj.get_client()
		try:
			validator.validate_otp(code)
		except:
			error_list['Code_required'] = "Code is required"
		if not error_list['Code_required']:
			try:
				telegram_obj.get_verified(client,int(code),request.session['phone_hash_code'])
				request.session['registration']  = True
			except:
				error_list['wrong_code']= 'Code is invalid '
				request.session['registration']  = False

		if request.session['registration'] and not error_list['Code_required']:
			registrationform.save()
			return redirect('/users/')

	context = {
		'code_required':error_list['Code_required'],
		'wrong_code':error_list['wrong_code']
		}

	return render(request,'verification.html',context)

def users(request):
	if 'login' in request.session or 'registration' in request.session:
		telegram_user_form  = Telegram_users_form(request.POST or None,error_class = DivErrorList)
		login_user = request.session['username']
		Telegram_users_data = Telegram_users.objects.all().filter(login_user = login_user).values
		cctv_data = CCTV.objects.all().filter(login_user = login_user).values
		run_all_detector(login_user)
		context = {
			'telegram_user_form_add':telegram_user_form,
			'username':request.session['username'],
			'Telegram_users_datas':Telegram_users_data,
			'cctv_datas':cctv_data,

		}
		return render(request,'users.html',context)
	else:
		return redirect('/')


def add_users(request):
	if 'login' in request.session or 'registration' in request.session:

		telegram_user_form  = Telegram_users_form(request.POST or None,error_class = DivErrorList)
		login_user = request.session['username']
		run_all_detector(login_user)
		Telegram_users_data = Telegram_users.objects.all().filter(login_user = login_user).values
		error_list = {}
		error_list['Group_not_exist'] = ''
		error_list['User_exist'] = ''
		error_list['User_notExist'] = ''
		error_list['Username_required']= ''
		error_list['group_name_required'] = ''
		if request.method == "POST":
			username = request.POST['username']
			group_name = request.POST['group_name']
			validator = ValidationRules()
			phone = Customer.objects.values_list('PhoneNumber').filter(username = request.session['username'])[0][0]
			if not username:
				error_list['Username_required'] = 'Username is required'
			if not group_name:
				error_list['group_name_required'] = 'Group Name is required'
			if not error_list['Username_required'] and not error_list['group_name_required']:
				telegram_obj = Messanger(phone)
				tele_client = telegram_obj.get_client()
				try:
					telegram_obj.get_groupid(tele_client,group_name)
					group_exist = True
				except ValidationError:
					error_list['Group_not_exist'] = 'Group does not exist'
					group_exist = False

				try:
					if group_exist:
						telegram_obj.user_exist(tele_client,username,group_name)
				except ValidationError:
					error_list['User_exist'] = 'user already exist'
				try:
					telegram_obj.username_exist(tele_client,username)
				except:
						error_list['User_notExist'] = "User does not exist"

				if not error_list['User_exist'] and not error_list['Group_not_exist'] and not error_list['User_notExist']:
					telegram_obj.add_users(tele_client,username,group_name)
					telegram_data = telegram_user_form.save(commit= False)
					telegram_data.save()
				tele_client.disconnect()

		context = {
			'telegram_user_form_add':telegram_user_form,
			'username':request.session['username'],
			'Group_not_exist':error_list['Group_not_exist'],
			'User_already_exist':error_list['User_exist'],
			'User_not_exist':error_list['User_notExist'],
			'Telegram_users_datas':Telegram_users_data,
			'login_user':login_user,
			'Username_required':error_list['Username_required'],
			'group_name_required':error_list['group_name_required']

		}

		return render(request,'users.html',context)
	else:
		return redirect('/')

def edit_user(request,username):
	if 'login' in request.session or 'registration' in request.session:
		telegram_user_form  = Telegram_users_form(request.POST or None,error_class = DivErrorList)
		login_user = request.session['username']
		run_all_detector(login_user)
		Telegram_users_data = Telegram_users.objects.all().filter(login_user = login_user).values
		error_list = {}
		error_list['User_exist'] = ''
		error_list['Group_not_exist'] = ''
		error_list['User_notExist'] = ''

		if request.method  == 'POST':


			new_username = request.POST['username']
			new_group_name = request.POST['group_name']
			login_user = request.session['username']
			validator = ValidationRules()

			phone = Customer.objects.values_list('PhoneNumber').filter(username = request.session['username'])[0][0]
			telegram_obj = Messanger(phone)
			tele_client = telegram_obj.get_client()
			try:
				telegram_obj.get_groupid(tele_client,new_group_name)
				group_exist = True
			except ValidationError:
				error_list['Group_not_exist'] = 'Group does not exist'
				group_exist = False

			try:
				if group_exist:
					telegram_obj.user_exist(tele_client,username,new_group_name)
			except ValidationError:
				error_list['User_exist'] = 'user already exist'
			try:
				telegram_obj.username_exist(tele_client,username)
			except:
					error_list['User_notExist'] = "User don't exist"

			if not error_list['User_exist'] and not error_list['Group_not_exist'] and not error_list['User_notExist']:
				updated_values = Telegram_users.objects.get(username = username)
				updated_values.username = new_username
				updated_values.group_name = new_group_name
				updated_values.save()
				telegram_obj.add_users(tele_client,username,new_group_name)
			tele_client.disconnect()
		context = {
			'telegram_user_form_edit':telegram_user_form,
			'username':request.session['username'],
			'Group_not_exist':error_list['Group_not_exist'],
			'User_already_exist':error_list['User_exist'],
			'User_not_exist':error_list['User_notExist'],
			'Telegram_users_datas':Telegram_users_data,
		}
		return render(request,'edit_users.html',context)
	else:
		return redirect('/')

def delete_user(request,username,group_name):
	if 'login' in request.session or 'registration' in request.session:
		Telegram_users_data_delete = Telegram_users.objects.all().filter(username= username,group_name = group_name).delete()
		error_list = {}
		error_list['User_exist'] = ''
		error_list['Group_not_exist'] = ''
		error_list['User_notExist'] = ''
		telegram_user_form  = Telegram_users_form(request.POST or None,error_class = DivErrorList)
		login_user = request.session['username']
		run_all_detector(login_user)
		Telegram_users_data = Telegram_users.objects.all().filter(login_user = login_user).values
		phone = Customer.objects.values_list('PhoneNumber').filter(username = request.session['username'])[0][0]
		telegram_obj = Messanger(phone)
		tele_client = telegram_obj.get_client()
		telegram_obj.delete_user(tele_client,username,group_name)
		context = {
			'telegram_user_form_add':telegram_user_form,
			'username':request.session['username'],
			'Telegram_users_datas':Telegram_users_data,
			'Group_not_exist':error_list['Group_not_exist'],
			'User_already_exist':error_list['User_exist'],
			'User_not_exist':error_list['User_notExist'],
		}
		return redirect('users')
	else:
		return redirect('/')

def cctv_view(request):
	if 'login' in request.session or 'registration' in request.session:
		cttv_forms = Cttv_forms(request.POST or None,error_class = DivErrorList)
		login_user = request.session['username']
		run_all_detector(login_user)
		cctv_data = CCTV.objects.all().filter(login_user = login_user).values
		context = {
			'cttv_form' :cttv_forms,
			'cctv_datas':cctv_data,
			'login_user':login_user
		}
		return render(request,'cctv_view.html',context)
	else:
		return redirect('/')




def add_cctv(request):
	if 'login' in request.session or 'registration' in request.session:
		cttv_forms = Cttv_forms(request.POST or None,error_class = DivErrorList)
		login_user = request.session['username']
		run_all_detector(login_user)
		cctv_data = CCTV.objects.all().filter(login_user = login_user).values
		errorList  = {}
		errorList['Server_url_required'] = ''
		errorList['detection_validator'] = ''
		errorList['cctv_name_validation'] = ''
		errorList['cctv_name_exist'] = ''
		errorList['Server_url_valid'] = ''

		if request.method == 'POST':
			cctv_name = request.POST['cctv_name']
			Server_url = request.POST['server_url']
			login_user = request.session['username']
			try:
				mask_detection = request.POST['mask_detection']
			except :
				mask_detection = 'off'
			try:
				social_detection = request.POST['social_distance']
			except :
				social_detection = 'off'

			validator = ValidationRules()
			try:
				validator.server_url_required(Server_url)
			except ValidationError:
				errorList['Server_url_required'] = 'Server_url is required'
			try:
				validator.validate_detection_option(mask_detection,social_detection)
			except ValidationError:
				errorList['detection_validator'] = 'One of the option is required'
			try:
				validator.cctv_name_required(request.POST['cctv_name'])
			except:
				errorList['cctv_name_validation'] = 'CCTV name is requied'

			try:
				validator.cctv_name_exist(request.POST['cctv_name'])
			except:
				errorList['cctv_name_exist'] = 'CCTV name already exist'
			try:
				validator.check_urls(request.POST['server_url'])

			except:
				errorList['Server_url_valid'] = 'Server url not valid'


			if  not  errorList['Server_url_required']  and not errorList['detection_validator'] and not errorList['cctv_name_validation'] and not errorList['cctv_name_exist'] and not errorList['Server_url_valid']:
				cctv = cttv_forms.save(commit = False)
				cctv.save()



		context = {
			'cttv_form' :cttv_forms,
			'server_url_required':errorList['Server_url_required'],
			'Detection_required':errorList['detection_validator'],
			'cctv_name_validation':errorList['cctv_name_validation'],
			'cctv_name_exist':errorList['cctv_name_exist'],
			'server_url_valid':errorList['Server_url_valid'],
			'login_user':login_user,
			'cctv_datas':cctv_data,
		}
		return render(request,'cctv_view.html',context)
	else:
		return redirect('/')

def display_all_camera(request):
	if 'login' in request.session or 'registration' in request.session:
		cttv_forms = Cttv_forms(request.POST or None,error_class = DivErrorList)
		login_user = request.session['username']
		run_all_detector(login_user)
		cctv_data = CCTV.objects.all().filter(login_user = login_user).values
		context = {
			'cttv_form' :cttv_forms,
			'cctv_datas':cctv_data,

		}
		return render(request,'display_all_camera.html',context)
	else:
		return redirect('/')


def gen_predistraion(user,camera):
	while True:
		frame = camera.get_pedistran_frame(user)
		yield (b'--frame\r\n'
				b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


def predistraion_feed(request,predistraion_camera_ip):
	return StreamingHttpResponse(gen_predistraion(request.session['username'],LiveWebCam(predistraion_camera_ip)),
					content_type='multipart/x-mixed-replace; boundary=frame')


def gen_mask(user,camera):
	while True:
		frame = camera.get_mask_frame(user)
		yield (b'--frame\r\n'
				b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


def mask_feed(request,mask_camera_ip):
	return StreamingHttpResponse(gen_mask(request.session['username'],LiveWebCam(mask_camera_ip)),
					content_type='multipart/x-mixed-replace; boundary=frame')




def run_all_detector(login_user):
	server_data = CCTV.objects.all().filter(login_user = login_user)
	for data in server_data:
		if data.mask_detection:
			schedule.every().second.do(run_mask_detector,username = login_user,camera_ip = data.server_url)
		stop_run_continuously = run_continuously()
		time.sleep(3)
		if data.social_distance:
			schedule.every().second.do(run_social_detector,username = login_user,camera_ip = data.server_url)




def delete_cctv(request,cctv_name):
	if 'login' in request.session or 'registration' in request.session:
		login_user = request.session['username']
		run_all_detector(login_user)
		cttv_forms = Cttv_forms(request.POST or None,error_class = DivErrorList)
		cctv_data_delete = CCTV.objects.filter(cctv_name = cctv_name).delete()
		cctv_data = CCTV.objects.all()
		context = {
			'cttv_form' :cttv_forms,
			'cctv_datas':cctv_data,

		}
		return redirect('cctv_view')
	else:
		return redirect('/')

def edit_cctv(request,cctv_name):
	if 'login' in request.session or 'registration' in request.session:
		login_user = request.session['username']
		run_all_detector(login_user)
		cttv_forms = Cttv_forms(request.POST or None,error_class = DivErrorList)
		cctv_data = CCTV.objects.all().filter(cctv_name= cctv_name).values
		errorList  = {}
		errorList['Server_url_required'] = ''
		errorList['detection_validator'] = ''
		errorList['cctv_name_validation'] = ''
		if request.method == 'POST':
			Server_url = request.POST['server_url']
			new_cctv_name = request.POST['cctv_name']
			try:
				mask_detection = request.POST['mask_detection']
			except :
				mask_detection = 'off'
			try:
				social_detection = request.POST['social_distance']
			except :
				social_detection = 'off'

			validator = ValidationRules()
			try:
				validator.server_url_required(Server_url)
			except ValidationError:
				errorList['Server_url_required'] = 'Server_url is required'
			try:
				validator.validate_detection_option(mask_detection,social_detection)
			except ValidationError:
				errorList['detection_validator'] = 'One of the option is required'
			try:
				validator.cctv_name_required(new_cctv_name)
			except:
				errorList['cctv_name_validation'] = 'CCTV name is requied'

			if  not  errorList['Server_url_required']  and not errorList['detection_validator'] and not errorList['cctv_name_validation']:
				update_values = CCTV.objects.get(cctv_name = cctv_name)
				update_values.cctv_name = new_cctv_name
				update_values.server_url = Server_url
				if mask_detection == 'on':
					mask_detection = True
				else:
					mask_detection = False
				update_values.mask_detection = mask_detection
				if social_detection == 'on':
					social_detection = True
				else:
					social_detection = False

				update_values.social_distance = social_detection

				update_values.save()
				return redirect('/cctv_view/')
		cttv_forms = Cttv_forms(request.POST or None,error_class = DivErrorList)


		context = {
			'cttv_form' :cttv_forms,
			'server_url_required':errorList['Server_url_required'],
			'Detection_required':errorList['detection_validator'],
			'cctv_name_validation':errorList['cctv_name_validation'],
			'cctv_datas':cctv_data,
		}
		return render(request,'edit_cctv.html',context)
	else:
		return redirect('/')