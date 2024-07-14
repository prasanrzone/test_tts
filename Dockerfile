# Use an official Python runtime as a parent image
FROM python:3.10.12-buster
# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    portaudio19-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8000 for the FastAPI app to be accessible
EXPOSE 8000

# Command to run the FastAPI app
CMD ["uvicorn", "server_:app", "--host", "0.0.0.0", "--port", "8000"]
