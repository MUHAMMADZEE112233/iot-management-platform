FROM python:3.9
ENV PYTHONDONTWRITEBYTECODE 1
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
RUN apt-get update && apt-get install -y postgresql-client
COPY . /code/
CMD python manage.py makemigrations && python manage.py migrate && python manage.py runserver 0.0.0.0:8000
