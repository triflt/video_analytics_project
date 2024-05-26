HOST = 'localhost'
PORT = 29092
FRAMES_TOPIC = 'frames'
DB_PASSWORD = 'postgres'
DB_USER = 'postgres'
DB_NAME = 'video_analytics'
MODEL_PATH = 'yolov8n.pt'

class States:
    PROCESSING = 'video_processing'
    INFERENCING = 'video_inferencing'