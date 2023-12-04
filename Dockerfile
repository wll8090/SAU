FROM python:3

WORKDIR /main

RUN python3 -m pip install --upgrade pip
RUN pip install flask
RUN pip install ldap3
RUN pip install flask_cors
RUN mkdir main

EXPOSE 5001/tcp

RUN ["python3","/main/app_SAU.py"]