import os
import cv2
import json
import base64
import uvicorn
from kafka import KafkaProducer
from fastapi import FastAPI, File, UploadFile
from tempfile import NamedTemporaryFile

import database.db as db
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
        value_serializer=lambda v: json.dumps(v).encode("utf-8"), 
        api_version=config.API_VERSION
    )

@app.post("/prediction/")
def post_video(file: UploadFile = File(...)):
    temp = NamedTemporaryFile(delete=False)
    result = 'no_result'
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
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps
        print(f'FPS: {fps}; Frame count: {frame_count}; Duration: {duration}')
        while cap.isOpened():
            success, frame = cap.read()
            if success:
                _, encoded_frame = cv2.imencode('.jpg', frame)
                preprocessed_frame = base64.b64encode(encoded_frame.tobytes()).decode('utf-8')
                data = {'frame': preprocessed_frame,
                        'video_id': result[0],
                        'frame_count': frame_count}
                producer.send(config.FRAMES_TOPIC, data)
            else:
                break

    except Exception as exept:
        print(exept)
        return {"message": "There was an error processing the file"}
    finally:
        os.remove(temp.name)
        return {"id": str(result[0])}

@app.get("/states/{video_id}")
def get_video_status(video_id: str):
    try:
        result = db.get_state(video_id)
        return {"state": str(result[0])}
    except ValueError as error:
        return {"error": error}

@app.get("/prediction/{video_id}")
def get_inference_result(video_id: str):
    try:
        result = db.select_inference_result(video_id)
        return {"result": {id_frame + 1: result[id_frame][0] for id_frame in range(len(result))}}
    except ValueError as error:
        return {"error": error}


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
    try:
        db_engine = db.get_db_engine().connect()
    except Exception as e:
        print(e)

