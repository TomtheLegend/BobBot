FROM python:3.6-alpine
EXPOSE 5000

# create directory
RUN mkdir /bobbot
WORKDIR /bobbot

# install requirements
ADD ./requirements.txt /bobbot
RUN pip install -r requirements.txt

# to add secrets.

ADD ./BobMain.py /bobbot

CMD [ "python", "BobMain.py" ]