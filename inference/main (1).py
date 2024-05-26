import logging
from unittest import result
import cv2
from cv2.typing import MatLike
import numpy as np
import typing as tp

from ultralytics import YOLO
import json
import base64
from kafka import KafkaConsumer, KafkaProducer
from typing import TypedDict
from ultralytics.utils.plotting import Annotator
import time
import os


PREDICTION_TOPIC = os.getenv("PREDICTION_TOPIC", "prediction")
IMAGES_TOPIC = os.getenv("IMAGES_TOPIC", "frames-splitted")
COMMAND_TOPIC = os.getenv("COMMAND_TOPIC", default="cmd-prediction")
CMD_RESPONSE_TOPIC = os.getenv("CMD_RESPONSE_TOPIC", default="responses")
KAFKA_BROKERS = os.getenv("KAFKA_BROKERS", "localhost:9091")
MODEL_PATH = os.getenv("YOLO_PATH", default="./models/yolov8n.pt")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)


logger.info(PREDICTION_TOPIC)
logger.info(IMAGES_TOPIC)
logger.info(KAFKA_BROKERS)


class PredictionResult(TypedDict):
    VideoId: int
    FrameId: str
    Frame: str  # base64 encoded image
    Results: dict  # YOLO results


class StatusMetadata(TypedDict):
    Frames: int


class Heartbeat(TypedDict):
    VideoId: int
    Metadata: StatusMetadata


class Predictor:
    def __init__(self, model: YOLO) -> None:
        self.model = model

    def inference(self, img: MatLike) -> np.ndarray[tp.Any, np.dtype[tp.Any]]:
        """Производит inference модели на изображении и возвращает изображение с наложенными bounding box'ами

        Args:
            img (MatLike): изображение в формате cv2

        Returns:
            np.ndarray[tp.Any, np.dtype[tp.Any]]: изображение с наложенными bounding box'ами
        """
        results = self.model(img)

        for r in results:
            annotator = Annotator(img)

            boxes = r.boxes
            for box in boxes:
                b = box.xyxy[0]
                c = box.cls
                annotator.box_label(
                    box=b,
                    label=self.model.names[int(c)],
                )

        return annotator.result()


class Controller:
    def __init__(
        self, predictor: Predictor, consumer: KafkaConsumer, producer: KafkaProducer
    ):
        """
        Args:
            predictor (Predictor): объект класса Predictor для предсказаний
            consumer (KafkaConsumer): kafka consumer с топиками IMAGES_TOPIC, COMMAND_TOPIC
            для получения изображений и команд от оркестратора
            producer (KafkaProducer): kafka producer для отправки результатов предсказаний и ответов на команды
        """
        self.predictor: Predictor = predictor
        self.consumer: KafkaConsumer = consumer
        self.producer: KafkaProducer = producer

        self.removed_video_ids = set()
        self.video_states: dict[int, int] = {}

    def _process_image(self, img: str) -> str:
        """Производит inference модели на изображении и возвращает результаты в виде base64 строки

        Args:
            img str: изображение в формате base64

        Returns:
            str: base64 строка с результатами предсказаний
        """
        img = base64.b64decode(img)  # type: ignore
        nparr = np.fromstring(img, np.uint8)  # type: ignore

        img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        result = self.predictor.inference(img_np)
        return base64.b64encode(cv2.imencode(".jpg", result)[1]).decode(  # type: ignore
            "utf-8"
        )

    def _send_heartbeat(self, video_id: int, frames: int) -> None:
        """Отправляет сообщение с информацией о количестве обработанных кадров

        Args:
            video_id (int): id видео
            frames (int): количество обработанных кадров
        """
        self.producer.send(
            CMD_RESPONSE_TOPIC,
            headers=[
                ("service", b"prediction"),
                ("type", b"healthcheck"),
            ],
            value=Heartbeat(
                VideoId=video_id,
                Metadata=StatusMetadata(
                    Frames=frames,
                ),
            ),
        )

    def _send_remove_response(self, video_id: int) -> None:
        """Отправляет ответ на команду остановки обработки видео

        Args:
            video_id (int): id видео
        """
        self.producer.send(
            CMD_RESPONSE_TOPIC,
            headers=[
                ("service", b"prediction"),
                ("type", b"remove"),
            ],
            value={"VideoId": video_id, "Status": "DONE"},
        )

    def _send_prediction_result(self, video_id: int, frame_id: str, frame: str) -> None:
        """Отправляет результаты предсказаний

        Args:
            video_id (int): id видео
            frame_id (str): id кадра
            frame (str): base64 строка с изображением
        """
        self.producer.send(
            PREDICTION_TOPIC,
            headers=[("service", b"prediction")],
            value=PredictionResult(
                VideoId=video_id,
                FrameId=frame_id,
                Frame=frame,
                Results={},
            ),
        )

    def run(self):
        for message in self.consumer:
            print(message.topic)
            if (
                message.topic == IMAGES_TOPIC
                and message.value["VideoId"] not in self.removed_video_ids
            ):
                if message.value["VideoId"] not in self.video_states:
                    self.video_states[message.value["VideoId"]] = 0

                result = self._process_image(message.value["RawFrame"])
                self._send_prediction_result(
                    video_id=message.value["VideoId"],
                    frame_id=message.value["FrameId"],
                    frame=result,
                )

                self.video_states[message.value["VideoId"]] += 1

                if self.video_states[message.value["VideoId"]] % 5 == 0:
                    self._send_heartbeat(
                        video_id=message.value["VideoId"],
                        frames=self.video_states[message.value["VideoId"]],
                    )

            elif message.topic == COMMAND_TOPIC:
                video_id, command = message.value["VideoId"], message.value["Command"]
                match command:
                    case "remove":
                        self.removed_video_ids.add(video_id)
                        self._send_remove_response(video_id)
                    case _:
                        logger.error(f"Unknown command: {command}")


def main():
    logger.info(f"loading yolov from {MODEL_PATH}")
    model = YOLO(MODEL_PATH, verbose=False)
    logger.info("loaded ml")

    image_consumer = KafkaConsumer(
        IMAGES_TOPIC,
        bootstrap_servers=KAFKA_BROKERS,
        auto_offset_reset="latest",
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    )

    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKERS,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )

    controller = Controller(
        predictor=Predictor(model),
        consumer=image_consumer,
        producer=producer,
    )

    controller.run()


if __name__ == "__main__":
    main()
