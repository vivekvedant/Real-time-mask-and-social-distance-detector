from telethon.sync import TelegramClient
from django.core.exceptions import ValidationError
from telethon.tl.functions.messages import AddChatUserRequest
import asyncio
from telethon.tl.functions.messages import  GetDialogsRequest
from telethon.tl.types import InputPeerEmpty
import os
from main.models import Customer, CCTV, Telegram_users
import glob
from alchemysession import AlchemySessionContainer
from sqlalchemy.engine import url as sa_url
import sqlalchemy
from telethon.tl.types import PeerUser

class Messanger:
    def __init__(self,user_number):
        self.api_id = 3105537
        self.api_hash  = '013bcb2c5a2c2e4af00c3ddc379d0fcb'
        self.phone = user_number
        
        
     
    def get_client(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop) 
        my_sqlalchemy_engine = sqlalchemy.create_engine("postgresql+psycopg2://telethon_user:postgres@telethon_db:5432/telethon")
        container = AlchemySessionContainer(engine=my_sqlalchemy_engine)
        session = container.new_session(self.phone)
        client = TelegramClient(session, self.api_id, self.api_hash, loop=loop)
        client.connect()
        return client
     
    def get_otp(self,client):
        otp_sended = client.send_code_request(self.phone)
        return otp_sended.phone_code_hash

    def get_verified(self,client,otp,phone_code_hash):
        return client.sign_in(self.phone,otp,phone_code_hash   = phone_code_hash)

    def get_groupid(self,client,group_name):
        dialog = client.get_dialogs()
        for d in dialog:
            
            if d.title == group_name:
                group_id = d.entity.id
                break
            else:
                group_id = None
        if  group_id == None:
             raise  ValidationError("Group don't exist")
        else:
            return group_id
            
    
    def user_exist(self,client,username,group_name):
        group_id = self.get_groupid(client,group_name)
        users = client.iter_participants(group_id)
        for user in users:
            if  user.username != None:
                if username.lower()  ==  user.username.lower():
                    user_exist_checker = True
                else:
                    user_exist_checker = False
            
            if user_exist_checker:
                raise  ValidationError("User already exists")

        

    def username_exist(self,client,username): 
        try:
            client.get_input_entity(username)   
        except:
             raise ValidationError("User does not exist")

        

    def add_users(self,client,username,group_name):
        group_id = self.get_groupid(client,group_name)
        client(AddChatUserRequest(
            group_id,
            username,
            fwd_limit=50
        ))
        

    def delete_user(self,client,username,group_name):
         group_id = self.get_groupid(client,group_name)
         client.kick_participant(group_id,username)
                    

def send_image(username):
    image_urls = glob.glob(f"./static/detection/{username}",recursive=True)
    Telegram_users_data = Telegram_users.objects.all().filter(login_user = username)
    user_data = Customer.objects.all().filter(username = username)

    for(tele_user,user_data) in zip(Telegram_users_data,user_data):    
        user_phone = user_data.PhoneNumber
        group_name = tele_user.group_name
        telegram_obj = Messanger(user_phone)
        tele_client = telegram_obj.get_client()
        tele_client.connect()
        for image_url in image_urls:
            tele_client.send_message(group_name,file = image_url)
            os.remove(image_url)
        tele_client.disconnect()
