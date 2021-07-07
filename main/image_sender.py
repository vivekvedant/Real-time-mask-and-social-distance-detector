import threading
import time
import schedule
import glob
from main.models import Customer, CCTV, Telegram_users
from main.telegram import Messanger
import os
import cv2
from main.object_predictors import Predictors

def run_continuously(interval=1):
    """Continuously run, while executing pending jobs at each
    elapsed time interval.
    @return cease_continuous_run: threading. Event which can
    be set to cease continuous run. Please note that it is
    *intended behavior that run_continuously() does not run
    missed jobs*. For example, if you've registered a job that
    should run every minute and you set a continuous run
    interval of one hour then your job won't be run 60 times
    at each interval but only once.
    """
    cease_continuous_run = threading.Event()

    class ScheduleThread(threading.Thread):
        @classmethod
        def run(cls):
            while not cease_continuous_run.is_set():
                schedule.run_pending()
                time.sleep(interval)

    continuous_thread = ScheduleThread()
    continuous_thread.start()
    return cease_continuous_run


def send_image(username):
    image_urls = glob.glob(f"./static/detection/{username}/*",recursive=True)
    Telegram_users_data = Telegram_users.objects.filter(login_user = username)
    user_data = Customer.objects.all().filter(username = username)
    group_names = []
    for d in Telegram_users_data:
        group_names.append(d.group_name)

    for(tele_user,user_data) in zip(Telegram_users_data,user_data):    
        user_phone = user_data.PhoneNumber
        # group_name = tele_user.group_name
        telegram_obj = Messanger(user_phone)
        tele_client = telegram_obj.get_client()
        tele_client.connect()
        for image_url in image_urls:
            for group_name in group_names:
                tele_client.send_message(group_name,file = image_url)
            os.remove(image_url)
        tele_client.disconnect()

def run_mask_detector(username,camera_ip):
    server = cv2.VideoCapture(camera_ip)
    detectors= Predictors()
    success,imgNp = server.read()
    frame = detectors.get_mask_detector(imgNp,username)
    send_image(username = username)

def run_social_detector(username,camera_ip):
    server = cv2.VideoCapture(camera_ip)
    detectors= Predictors()
    success,imgNp = server.read()
    frame = detectors.get_pedistran_detector(imgNp,username)
    send_image(username = username)

