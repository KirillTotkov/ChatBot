FROM python:3.10-slim

RUN apt-get update -y

COPY requirements.txt /opt/app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt

COPY . /app

CMD ["python3", "bot.py"]