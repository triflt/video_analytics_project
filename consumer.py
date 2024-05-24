import asyncio
from aiokafka import AIOKafkaConsumer

import config
from utils import deserializer


async def consume():
    consumer = AIOKafkaConsumer(
        config.TOPIC,
        bootstrap_servers=f'{config.HOST}:{config.PORT}',
        value_deserializer=deserializer
    )
    await consumer.start()
    try:
        async for msg in consumer:
            print(
            "{}:{:d}:{:d}: key={} value={} timestamp_ms={}".format(
                msg.topic, msg.partition, msg.offset, msg.key, msg.value,
                msg.timestamp)
        )
    finally:
        await consumer.stop()


if __name__ == '__main__':
    asyncio.run(consume())