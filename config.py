from typing import Tuple

HOST: str = '127.0.0.1'
PORT: int = 29092
API_VERSION: Tuple[int, int, int] = (0, 11, 5)
FRAMES_TOPIC: str = 'frames'
DB_PASSWORD: str = 'postgres'
DB_USER: str = 'postgres'
DB_NAME: str = 'video_analytics'
MODEL_PATH: str = 'yolov8n.pt'


class States:
    """
    Class to define different states in the video processing pipeline.
    """
    
    PROCESSING: str = 'video_processing'
    INFERENCING: str = 'video_inferencing'
    FINISHED: str = 'video_inference_finished'