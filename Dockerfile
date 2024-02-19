FROM python:3.10

ENV PYTHONUNBUFFERED=1

RUN mkdir /code
WORKDIR /code

RUN apt-get update && apt-get install -y netcat-traditional
RUN pip install --upgrade pip

COPY requirements.txt /code/requirements.txt
RUN pip install -r requirements.txt

COPY . /code/

