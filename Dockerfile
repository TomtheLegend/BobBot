FROM python:3.8-buster
EXPOSE 5000

# create directory
RUN mkdir /bobbot
WORKDIR /bobbot

COPY . .

# install requirements
#RUN apt install zlib1g
# RUN apk add --no-cache gcc libc-dev unixodbc-dev zlib1g

RUN pip install -r requirements.txt

# to add secrets.


CMD [ "python", "BobMain.py" ]