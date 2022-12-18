import os
import time
import datetime
from ml.pipeline.faiss import FaissPipeline
import uuid
from environment import Environment
import json
from kafka import KafkaConsumer
from kafka import KafkaProducer
from common.storage_location import StorageLocation
from ml.pipeline.embed import EmbedPipeline
from common.logger import CommonLogger


class DatabaseConsumer:

    producer_conquer = None
    producer_combine = None
    storage_location = None
    faiss_pipeline = None
    consumer = None
    logger = CommonLogger()

    def consume(self, topics=None, storage_location=StorageLocation.LOCAL_DISK):
        self.consumer = KafkaConsumer(
            bootstrap_servers=Environment.kafka_bootstrap_servers,
            group_id=Environment.kafka_group_default,
            auto_offset_reset="earliest",
        )
        self.producer_conquer = KafkaProducer(
            bootstrap_servers=Environment.kafka_bootstrap_servers,
            key_serializer=str.encode,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )
        self.producer_combine = KafkaProducer(
            bootstrap_servers=Environment.kafka_bootstrap_servers,
            key_serializer=str.encode,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )
        self.logger.info(
            "Consuming topic: {} for group id: {}".format(
                topics, Environment.kafka_group_default
            )
        )
        self.storage_location = storage_location
        self.faiss_pipeline = FaissPipeline(storage_location=self.storage_location)
        try:
            self.logger.info("subscribe: ", topics)
            self.consumer.subscribe(topics)
            for msg in self.consumer:
                self.logger.info(
                    "consumed: ",
                    msg.topic,
                    msg.partition,
                    msg.offset,
                    msg.key,
                    msg.value,
                    msg.timestamp,
                )
                if msg.topic == Environment.kafka_topic_divide:
                    self.divide(msg.value)
                if msg.topic == Environment.kafka_topic_conquer:
                    self.conquer(msg.value)
                if msg.topic == Environment.kafka_topic_combine:
                    self.combine(msg.value)
        finally:
            self.consumer.close()

    def divide(self, message):
        start_time = time.time()
        batch_id = str(uuid.uuid4())
        items = json.loads(message)
        if self.storage_location == StorageLocation.LOCAL_DISK:
            directory = "{}/.processing".format(Environment.default_storage)
            if not os.path.exists(directory):
                os.makedirs(directory)
            target_path = "{}/{}.json".format(directory, batch_id)
            with open(target_path, "w") as outfile:
                outfile.write(json.dumps(items))
        for item in items:
            future_embed = self.producer_conquer.send(
                Environment.kafka_topic_conquer,
                key=item["index_id"],
                value={
                    "_id": item["_id"],
                    "source": batch_id,
                    "index_id": item["index_id"],
                    "text": item["column_value"],
                },
            )
            future_embed.get(timeout=60)
        self.producer_conquer.flush()
        self.logger.info(
            "database.consumer.divide-completed-in-{}-seconds".format(
                time.time() - start_time
            )
        )

    def conquer(self, message):
        start_time = time.time()
        item = json.loads(message)
        (
            text_embedding,
            context_embedding,
            label_embedding,
            text_generated,
            labels_generated,
        ) = EmbedPipeline().encode(text=item["text"])
        item["embedding"] = json.dumps(text_embedding.tolist())
        item["context_embedding"] = json.dumps(context_embedding.tolist())
        item["label_embedding"] = json.dumps(label_embedding.tolist())
        item["text_generated"] = text_generated
        item["labels_generated"] = labels_generated
        key = item["index_id"]
        future_emerge = self.producer_combine.send(
            Environment.kafka_topic_combine, key=key, value=item
        )
        future_emerge.get(timeout=60)
        self.producer_combine.flush()
        self.logger.info(
            "database.consumer.conquer-completed-in-{}-seconds".format(
                time.time() - start_time
            )
        )

    def combine(self, message):
        start_time = time.time()
        data = json.loads(message)
        if data.get("source") is None:
            return None
        batch_id = data["source"]
        if self.storage_location == StorageLocation.LOCAL_DISK:
            directory = "{}/.processing".format(Environment.default_storage)
            if not os.path.exists(directory):
                os.makedirs(directory)
            target_path = "{}/{}.json".format(directory, batch_id)
            if os.path.exists(target_path) is False:
                return None
        _id = data["_id"]
        items = json.load(open(target_path))
        item = [item for item in items if item.get("_id") == _id]
        if item is None or len(items) == 0:
            return None

        item = item[0]
        item["embedding"] = data["embedding"]
        item["label_embedding"] = data["label_embedding"]
        item["context_embedding"] = data["context_embedding"]
        item["text_generated"] = data["text_generated"]
        item["labels_generated"] = data["labels_generated"]

        if self.storage_location == StorageLocation.LOCAL_DISK:
            target_path = "{}/.processing/{}.json".format(
                Environment.default_storage, batch_id
            )
            with open(target_path, "w") as outfile:
                outfile.write(json.dumps(items))
        if self.batchHasCompleted(items) is True:
            database = items[0]["database"]
            index_id = items[0]["index_id"]
            self.faiss_pipeline.write(database=database, index_id=index_id, items=items)
            if os.path.exists(target_path):
                os.remove(target_path)
            self.logger.info(
                "database.consumer.combine-has-batched-completed-{}-seconds-during-{}".format(
                    time.time() - start_time, datetime.datetime.now()
                )
            )

        self.logger.info(
            "database.consumer.combine-completed-in-{}-seconds-during-{}".format(
                time.time() - start_time, datetime.datetime.now()
            )
        )

    def batchHasCompleted(self, items):
        completed = [item for item in items if item.get("embedding") is not None]
        return len(items) == len(completed) and len(completed) > 0
