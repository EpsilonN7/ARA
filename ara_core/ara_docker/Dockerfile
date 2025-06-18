# Use a slim version of Python
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Copy your Flask app into the container
COPY server.py .

# Install Flask and requests
RUN pip install flask requests

# install pyyaml for YAML support, and beautifulsoup4 for HTML parsing
RUN pip install pyyaml beautifulsoup4

# Expose the port your app runs on
EXPOSE 6969

# Command to run your Flask app
CMD ["python", "server.py"]
