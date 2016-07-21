FROM python:3.5
MAINTAINER datapunt@amsterdam.nl

ENV PYTHONUNBUFFERED 1

WORKDIR /tests
COPY requirements.txt /tests/
RUN pip install --no-cache-dir -r requirements.txt

COPY /src /tests/
