FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (cached layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create instance folder for SQLite DB
RUN mkdir -p /app/instance

EXPOSE 5000

ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV SECRET_KEY=change-this-in-production

CMD ["python", "app.py"]
