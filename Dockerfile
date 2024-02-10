# Use an official Python runtime as a parent image
FROM python:3.10.12-alpine

# Set the working directory in the container
WORKDIR /app

# If you're using requirements.txt:
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# If you're using Pipenv (uncomment these lines and comment out requirements.txt lines above):
# Install pipenv and dependencies from Pipfile
# COPY Pipfile Pipfile.lock /app/
# RUN pip install --upgrade pip && pip install pipenv
# RUN pipenv install --system --deploy --ignore-pipfile

# Copy the current directory contents into the container at /app
COPY ./app /app

# Make port 5001 available to the world outside this container
EXPOSE 5001
 
# Run app.py when the container launches
CMD ["python", "app.py"]