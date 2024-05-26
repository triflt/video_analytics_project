import cv2
import sys
import json
import base64
import numpy as np
from ultralytics import YOLO
from kafka import KafkaConsumer

sys.path.append('../')

import config
import db

def preprocessing(frame):
    resized_frame = cv2.resize(frame, (640, 480))
    return resized_frame

def predictor(frame): 
    results = model(frame)
    return results

def consume():
    consumer = KafkaConsumer(
        config.FRAMES_TOPIC,
        bootstrap_servers=f'{config.HOST}:{config.PORT}',
        value_deserializer=lambda m: json.loads(m.decode("utf-8"))
    )
    for message in consumer:
        print(message.topic)
        if message.topic == config.FRAMES_TOPIC:
            frame = message.value['frame']
            frame_bytes = base64.b64decode(frame)
            frame_array = np.frombuffer(frame_bytes, dtype=np.uint8)
            frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)
            prediction = predictor(frame)
            print(prediction)
            print(prediction[0].tojson())
            bboxes_prediction = prediction[0].tojson()
            print(bboxes_prediction)
            print(bboxes_prediction['boxes'])
            db.save_prediction(json.loads(bboxes_prediction))
            print(type(bboxes_prediction))
        else: 
            print('Doesn`t FRAMES_TOPIC')

        
if __name__ == "__main__":
    print('Runner started')
    model = YOLO(config.MODEL_PATH, verbose=False)
    print('Model loaded')
    consume()