import uvicorn
from aiokafka import AIOKafkaProducer
from fastapi import FastAPI
from sqlalchemy.sql import text

from utils import serializer
import config
from sqlalchemy import create_engine

def get_db_engine():
    return create_engine(f'postgresql://{config.DB_USER}:{config.DB_PASSWORD}@postgres:5432/{config.DB_NAME}')

'''import psycopg2

connection = psycopg2.connect(database="video_analytics", user="user", password="user", host="localhost", port=5432)
cursor = connection.cursor()'''

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "App Started"}

@app.on_event("shutdown")
async def shutdown_event():
    await producer.stop()

@app.on_event("startup")
async def startup_event():
    global producer
    producer = AIOKafkaProducer(
        bootstrap_servers=f'{config.HOST}:{config.PORT}',
        value_serializer=serializer,
        compression_type="gzip"
    )
    await producer.start()

@app.post("/videos/")
async def post_video(item: str):
    pass

@app.get("/videos/{video_id}")
async def get_video_status(video_id: str):
    result = db_engine.execute(text("SELECT state FROM first_table WHERE id=:id"), {"id": video_id})
    state = result.fetchone()
    if state:
        return {"state": state[0]}
    else:
        return {"message": "Item not found"}


if __name__ == '__main__':
    uvicorn.run(app, port=8000)
    try:
        db_engine = get_db_engine().connect()
    except Exception as e:
        print(e)

