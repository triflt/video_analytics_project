FROM python:3.9

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

WORKDIR /inference

COPY . /inference
COPY ../config.py /inference/config.py
COPY ../database/db.py /inference

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "runner.py"]