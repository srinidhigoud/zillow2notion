# Use a lightweight Python image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the app files
COPY . .

# Set up virtual environment inside Docker
RUN python3 -m venv venv && source venv/bin/activate

# Install dependencies from requirements.txt inside venv
RUN venv/bin/pip install --upgrade pip
RUN venv/bin/pip install -r requirements.txt

# Expose the Flask app port
EXPOSE 5000

# Run the Flask app using Gunicorn
CMD ["venv/bin/gunicorn", "-b", "0.0.0.0:5000", "app:app"]
