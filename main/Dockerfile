FROM python:3.10

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

RUN python manage.py makemigrations
RUN python manage.py migrate

EXPOSE 8000

ENV DJANGO_SETTINGS_MODULE=main.settings
ENV PYTHONUNBUFFERED=1

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
