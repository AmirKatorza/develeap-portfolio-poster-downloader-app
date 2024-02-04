# Use an official Python runtime as a parent image
FROM python:3.9-alpine

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# If you're using Pipenv:
# Install pipenv and dependencies from Pipfile
# RUN pip install --upgrade pip && pip install pipenv
# RUN pipenv install --system --deploy --ignore-pipfile

# If you're using requirements.txt (uncomment these lines and comment out Pipenv lines above):
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5001 available to the world outside this container
EXPOSE 5001

# Run app.py when the container launches
CMD ["python", "app.py"]