FROM python:3.9

# Update the package lists
RUN apt-get update

COPY . /video_analytics_project

WORKDIR /video_analytics_project

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]