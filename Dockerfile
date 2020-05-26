# syntax=docker/dockerfile:experimental
FROM python:3.8-buster
EXPOSE 5000

# create directory
RUN mkdir /bobbot
WORKDIR /bobbot

COPY . .

RUN --mount=type=secret,id=Settings.json cat /run/secrets/Settings

# install requirements
RUN pip install -r requirements.txt

CMD [ "python", "BobMain.py" ]