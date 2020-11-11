FROM python:3.8-slim

COPY . /app

WORKDIR /app

RUN python3 setup.py install

ENTRYPOINT ["myscript"]
