import cv2
import sys
import json
import base64
import numpy as np
from ultralytics import YOLO
from kafka import KafkaConsumer

sys.path.append('../')

import config
import database.db as db

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
    video_id, frame_counter = 0, 1
    for message in consumer:
        if message.topic == config.FRAMES_TOPIC:
            if video_id != message.value['video_id']:
                video_id = message.value['video_id']
                total_frames = message.value['frame_count']
                db.update_state(state=config.States.INFERENCING,
                                    video_id=video_id)
                print(f'Video {video_id} is inferencing')
            frame_counter += 1
            frame = message.value['frame']
            video_id = message.value['video_id']
            frame_bytes = base64.b64decode(frame)
            frame_array = np.frombuffer(frame_bytes, dtype=np.uint8)
            frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)
            preprocessed_frame = preprocessing(frame)
            prediction = predictor(preprocessed_frame)
            if len(prediction[0].boxes.xyxy) > 0:
                predicions = {"boxes": prediction[0].boxes.xyxy.tolist(),
                              "conf": prediction[0].boxes.conf.tolist(),
                              "cls": prediction[0].boxes.cls.tolist()}
            else: 
                predicions = {"boxes": ["no_detection"],
                              "conf": ["no_detection"],
                              "cls": ["no_detection"]}
            print('frame_counter: ', frame_counter)
            if frame_counter == total_frames - 1:
                db.update_state(state=config.States.FINISHED, video_id=video_id)
                frame_counter = 1

            db.save_prediction(predicions, video_id)
            
        else: 
            print('Doesn`t FRAMES_TOPIC')
        

        
if __name__ == "__main__":
    print('Runner started')
    model = YOLO(config.MODEL_PATH, verbose=False)
    print('Model loaded')
    consume()