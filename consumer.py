from kafka import KafkaConsumer

import config
from utils import deserializer


def consume():
    consumer = KafkaConsumer(
        config.TOPIC,
        bootstrap_servers=f'{config.HOST}:{config.PORT}',
        value_deserializer=deserializer
    )
    #consumer.start()
    try:
        for msg in consumer:
            print(
            "{}:{:d}:{:d}: key={} value={} timestamp_ms={}".format(
                msg.topic, msg.partition, msg.offset, msg.key, msg.value,
                msg.timestamp)
        )
    finally:
        consumer.stop()


if __name__ == '__main__':
    consume()