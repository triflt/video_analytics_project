import asyncio
import json
from aiokafka import AIOKafkaConsumer

import config


def deserializer(serialized):
    """
    Десериализатор получаемых данных
    """
    return json.loads(serialized)


async def event_handler(value):
    """
    Обработчик события. Как только мы получаем новое сообщение,
    будет отрабатывать данная функция
    """
    print(f"Temperature: {value['temp']}, weather: {value['weather']}")


async def consume():
    consumer = AIOKafkaConsumer(
        config.WEATHER_TOPIC,
        bootstrap_servers=f'{config.HOST}:{config.PORT}',
        value_deserializer=deserializer
    )
    await consumer.start()
    try:
        async for msg in consumer:
            await event_handler(msg.value)
    finally:
        await consumer.stop()


if __name__ == '__main__':
    asyncio.run(consume())