HOST = 'localhost'
HOST = '127.0.0.1'
PORT = 29092
API_VERSION = (0,11,5)
FRAMES_TOPIC = 'frames'
DB_PASSWORD = 'postgres'
DB_USER = 'postgres'
DB_NAME = 'video_analytics'
MODEL_PATH = 'yolov8n.pt'


class States:
    PROCESSING = 'video_processing'
    INFERENCING = 'video_inferencing'
    FINISHED = 'video_inference_finished'