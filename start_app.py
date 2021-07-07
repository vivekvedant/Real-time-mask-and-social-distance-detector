import os
import webbrowser


#build the container
print("=========================================== \n")
print("Building django container \n")
print("=========================================== \n")
os.system("docker build --tag django_app . ")





#run the container
print("=========================================== \n")
print("create database \n")
print("=========================================== \n")
os.system("docker-compose up -d")


#migrate table in database
print("=========================================== \n")
print("Migrating table into database \n")
print("=========================================== \n")
os.system( "docker-compose run django_app /usr/local/bin/python manage.py migrate")



#launch app
print("=========================================== \n")
print("Lunching App \n")
print("=========================================== \n")
webbrowser.open('http://localhost:8000/')
