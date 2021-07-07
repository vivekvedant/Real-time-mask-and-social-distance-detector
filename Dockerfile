FROM python:3.7
RUN apt update && apt-get upgrade -y
RUN apt install libgl1-mesa-glx -y
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/
# RUN python manage.py makemigrations 
# RUN python manage.py migrate


