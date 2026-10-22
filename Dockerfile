# Start from an official Python image with a small Linux base
FROM python:3.12-slim

# All following commands run inside this folder in the container
WORKDIR /app

# Don't write .pyc cache files, and print logs immediately
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Copy only the dependency list first, so Docker can cache the install step
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY app ./app
COPY templates ./templates
COPY static ./static

# Run as a normal user instead of root, for security
RUN useradd --create-home appuser
USER appuser

# Document the port the app listens on
EXPOSE 5000

# Start the app with gunicorn, listening on all interfaces inside the container
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app.main:app"]