# Use the official Python image
FROM python:3.10.0-buster

# Set the working directory
WORKDIR /app

# Copy the requirements.txt file
COPY requirements.txt .

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Python files into the container
COPY . .

# Install cron
RUN apt-get update && apt-get -y install cron

# Copy the cron file
COPY crontab /etc/cron.d/crontab

# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/crontab

# Apply cron job
RUN crontab /etc/cron.d/crontab

# Create the log file to be able to run tail
RUN touch /var/log/cron.log

# Set the command to be run when the container starts
CMD cron && tail -f /var/log/cron.log
