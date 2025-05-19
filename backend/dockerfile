# functions/archiemcp/Dockerfile
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
# Assuming main.py and any other necessary files are in the same directory as this Dockerfile
COPY main.py . 
# If you have other subdirectories or files, copy them as well, e.g.:
# COPY ./your_module /app/your_module

# Expose the port the app runs on
EXPOSE 8080

# Set environment variables (if any needed directly in the container beyond what Cloud Run provides)
# ENV GCP_PROJECT_ID=${GCP_PROJECT_ID} # These are better injected by Cloud Run service definition

# Command to run the application using Gunicorn
# It looks for an 'app' instance in a file named 'main.py'
CMD ["gunicorn", "-b", ":8080", "--workers", "1", "--threads", "8", "--timeout", "0", "main:app"]