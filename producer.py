import asyncio
import json
import random
from aiokafka import AIOKafkaProducer

import config


def serializer(value):
    """
    Обмен данными происходит в байтах, поэтому мы должны
    сначала перевести наше значение JSON, а затем в байты
    """
    return json.dumps(value).encode()


async def produce():
    producer = AIOKafkaProducer(
        bootstrap_servers=f'{config.HOST}:{config.PORT}',
        value_serializer=serializer,
        compression_type="gzip"
    )
    await producer.start()
    try:
        while True:
            data = {
                "temp": random.randint(10, 20),
                "weather": random.choice(("rainy", "sunny"))
            }
            await producer.send(config.WEATHER_TOPIC, data)
            await asyncio.sleep(random.randint(1, 5))
    finally:
        await producer.stop()


if __name__ == '__main__':
    asyncio.run(produce())