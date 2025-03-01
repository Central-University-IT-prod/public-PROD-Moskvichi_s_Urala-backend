FROM python:3.12.1-alpine3.19

WORKDIR /

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .