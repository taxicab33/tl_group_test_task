FROM python:3.11

WORKDIR /backend

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . /backend

CMD gunicorn backend.wsgi:application --bind 0.0.0.0:80 --workers=4
