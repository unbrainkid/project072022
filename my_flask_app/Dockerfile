FROM python:3.9
MAINTAINER Vladislav Stolbov 'vladissto@gmail.com'
RUN apt-get update -y
RUN apt-get install -y python-dev build-essential

ADD . /
WORKDIR /

RUN pip install -r requirements.txt
EXPOSE 5000
#ENTRYPOINT ['python-devon']
CMD python app.py
