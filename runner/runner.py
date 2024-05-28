import cv2
import sys
import json
import base64
import numpy as np
from typing import Dict, Any
from ultralytics import YOLO
from kafka import KafkaConsumer

sys.path.append('../')

import config
import database.db as db

def preprocessing(frame: np.ndarray) -> np.ndarray:
    """Preprocesses the input frame by resizing it to (640, 480) dimensions."""
    resized_frame = cv2.resize(frame, (640, 480))
    return resized_frame

def predictor(frame: np.ndarray, model: Any) -> Any:
    """Uses the YOLO model to predict on the frame."""
    results = model(frame)
    return results

def consume() -> None:
    """Reads frames from Kafka, processes the frames, and saves the predictions to the database."""
    consumer = KafkaConsumer(
        config.FRAMES_TOPIC,
        bootstrap_servers=f'{config.HOST}:{config.PORT}',
        value_deserializer=lambda m: json.loads(m.decode("utf-8"))
    )
    video_id, frame_counter = 0, 1
    model = YOLO(config.MODEL_PATH, verbose=False)
    
    for message in consumer:
        if message.topic == config.FRAMES_TOPIC:
            if video_id != message.value['video_id']:
                video_id = message.value['video_id']
                frame_counter = 1
                total_frames = message.value['frame_count']
                db.update_state(state=config.States.INFERENCING, video_id=video_id)
                print(f'Video {video_id} is inferencing')
                
            frame_counter += 1
            frame = message.value['frame']
            video_id = message.value['video_id']
            frame_bytes = base64.b64decode(frame)
            frame_array = np.frombuffer(frame_bytes, dtype=np.uint8)
            frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)
            preprocessed_frame = preprocessing(frame)
            prediction = predictor(preprocessed_frame, model)
            
            if len(prediction[0].boxes.xyxy) > 0:
                predictions = {
                    "boxes": prediction[0].boxes.xyxy.tolist(),
                    "conf": prediction[0].boxes.conf.tolist(),
                    "cls": prediction[0].boxes.cls.tolist()
                }
            else:
                predictions = {
                    "boxes": ["no_detection"],
                    "conf": ["no_detection"],
                    "cls": ["no_detection"]
                }
            
            print('frame_counter: ', frame_counter)
            
            if frame_counter == total_frames - 1:
                db.update_state(state=config.States.FINISHED, video_id=video_id)
                frame_counter = 1
                
            db.save_prediction(predictions, video_id)
        else:
            print('Doesn`t FRAMES_TOPIC')

if __name__ == "__main__":
    print('Runner started')
    consume()
