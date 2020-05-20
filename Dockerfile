FROM python:3.7-alpine
EXPOSE 5000

# create directory
RUN mkdir /bobbot
WORKDIR /bobbot

# install requirements
RUN pip -V
RUN pip install --upgrade pip
RUN pip -V
RUN apk add --no-cache gcc libc-dev unixodbc-dev
ADD ./requirements.txt /bobbot
RUN pip install -r requirements.txt

# to add secrets.

ADD ./BobMain.py /bobbot

CMD [ "python", "BobMain.py" ]