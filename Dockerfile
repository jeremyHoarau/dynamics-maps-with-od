FROM python:3.8-slim-buster
RUN apt-get update && apt-get install -y python3 python3-pip


WORKDIR /srv

COPY requirements.txt .
# install dependencies
RUN pip install -r requirements.txt

# copy the content of the local src directory to the working directory
COPY ./ .

EXPOSE 5080

CMD [ "uwsgi", "--ini","uwsgi.ini" ]