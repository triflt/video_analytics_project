import uvicorn
from kafka import KafkaProducer
from fastapi import FastAPI
from sqlalchemy.sql import text

from utils import serializer
from db import insert, select
import config
from sqlalchemy import create_engine

def get_db_engine():
    return create_engine(f'postgresql://{config.DB_USER}:{config.DB_PASSWORD}@postgres:5432/{config.DB_NAME}')

app = FastAPI()

@app.get("/")
def root():
    return {"message": "App Started"}

'''@app.on_event("shutdown")
def shutdown_event():

    return producer.stop()'''

@app.on_event("startup")
def startup_event():
    global producer
    producer = KafkaProducer(
        bootstrap_servers=f'{config.HOST}:{config.PORT}',
        value_serializer=serializer,
        compression_type="gzip"
    )
    #return producer.start()

@app.post("/videos/")
def post_video(state: str):
    insert(state)
    producer.send(config.TOPIC, state)

@app.get("/videos/{video_id}")
def get_video_status(video_id: str):
    return select(video_id)


if __name__ == '__main__':
    uvicorn.run(app, port=8000)
    try:
        db_engine = get_db_engine().connect()
    except Exception as e:
        print(e)

