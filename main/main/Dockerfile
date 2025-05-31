FROM python:3.10

WORKDIR /app

COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Migrate the database
RUN python manage.py makemigrations
RUN python manage.py migrate

# Expose port
EXPOSE 8000

# Set environment variables
ENV DJANGO_SETTINGS_MODULE=main.settings
ENV PYTHONUNBUFFERED=1

# Run the app
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
