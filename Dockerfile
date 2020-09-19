FROM python:3.7
RUN apt-get clean && apt-get -y update
RUN apt-get -y install python3-dev build-essential nano
ADD . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 5000