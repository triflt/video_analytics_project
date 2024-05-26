import os
import cv2
import json
import base64
import uvicorn
from kafka import KafkaProducer
from fastapi import FastAPI, File, UploadFile
from tempfile import NamedTemporaryFile

import db
#from inference import preprocessing
import config

def preprocessing(frame):
    resized_frame = cv2.resize(frame, (640, 480))
    return resized_frame

app = FastAPI()

@app.get("/")
def root():
    return {"message": "App Started"}

@app.on_event("startup")
def startup_event():
    global producer
    producer = KafkaProducer(
        bootstrap_servers=f'{config.HOST}:{config.PORT}',
        value_serializer=lambda v: json.dumps(v).encode("utf-8")
        #compression_type="gzip"
    )

@app.post("/videos/")
def post_video(file: UploadFile = File(...)):
    temp = NamedTemporaryFile(delete=False)
    try:
        try:
            contents = file.file.read()
            with temp as f:
                f.write(contents)
        except Exception as exept:
            print(exept)
            return {"message": "There was an error uploading the file"}
        finally:
            file.file.close()

        result = db.init_state(config.States.PROCESSING)
        cap = cv2.VideoCapture(temp.name)
        while cap.isOpened():
            success, frame = cap.read()
            if success:
                preprocessed_frame = preprocessing(frame)
                _, encoded_frame = cv2.imencode('.jpg', preprocessed_frame)
                preprocessed_frame = base64.b64encode(encoded_frame.tobytes()).decode('utf-8')
                #print(preprocessed_frame)
                data = {'frame': preprocessed_frame}
                producer.send(config.FRAMES_TOPIC, data)
                break

    except Exception as exept:
        print(exept)
        return {"message": "There was an error processing the file"}
    finally:
        os.remove(temp.name)
        return {"id": str(result[0])}

@app.get("/videos/{video_id}")
def get_video_status(video_id: str):
    try:
        result = db.get_state(video_id)
        return {"id": str(result[0])}
    except ValueError as error:
        return {"error": error}


if __name__ == '__main__':
    uvicorn.run(app, port=8000)
    try:
        db_engine = db.get_db_engine().connect()
    except Exception as e:
        print(e)

