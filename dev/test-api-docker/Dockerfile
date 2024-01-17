# Use an official Python runtime as a parent image
FROM python:3.10-alpine

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY test_api_app.py /app/
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh


# Install any needed packages specified in requirements.txt
RUN pip install  Flask nodered-forge

# Create a non-root user with UID 1000
RUN adduser -D -u 1000 user
USER user

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable
# Run app.py when the container launches
CMD ["/entrypoint.sh"]
