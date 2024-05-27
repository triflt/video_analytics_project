FROM python:3.9

EXPOSE 8000
# Update the package lists
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

COPY . /video_analytics_project

WORKDIR /video_analytics_project

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]