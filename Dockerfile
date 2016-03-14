FROM python:3.5
MAINTAINER datapunt@amsterdam.nl

ENV PYTHONUNBUFFERED 1

#EXPOSE 8000

#RUN apt-get update \
#	&& apt-get clean \
#	&& rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

WORKDIR /tests
COPY requirements.txt /tests/
RUN pip install --no-cache-dir -r requirements.txt

#USER datapunt
COPY /tests /tests/
