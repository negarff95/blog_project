# Use the official Python image from the Docker Hub
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /code

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && apt-get clean

# Install Python dependencies
COPY requirements.txt /code/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the Django project code into the Docker image
COPY . /code/

# Expose the ports for Django and MkDocs
EXPOSE 8000 8001

# Default command to run when the container starts
CMD ["sh", "-c", "mkdocs serve -a 0.0.0.0:8001 & python manage.py runserver 0.0.0.0:8000"]
