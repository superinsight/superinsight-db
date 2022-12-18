from common.logger import CommonLogger
import os
import json
from database.csv.helper import CsvHelper
from database.sql.helper import SqlHelper
from kafka import KafkaProducer
from environment import Environment
import uuid


class TrainRecommender:

    logger = None
    database = None
    producer = None

    def __init__(self, logger=None, handler=None, database=None):
        self.logger = CommonLogger(logger=logger, handler=handler)
        self.database = database
        self.producer = KafkaProducer(
            bootstrap_servers=Environment.kafka_bootstrap_servers,
            key_serializer=str.encode,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )

    def __del__(self):
        self.logger.info("ML.Train.TrainRecommender...")

    def initialize(self, sql, model_id=None):
        if model_id is None:
            model_id = uuid.uuid4().hex
        rows = SqlHelper(database=self.database).read(sql=sql, return_dict=True)
        self.produce(model_id=model_id, rows=rows)
        return model_id

    def produce(self, model_id, rows):
        messages = self.formatForStreaming(model_id=model_id, rows=rows)
        key = "{}_{}".format(self.database, model_id)
        for message in messages:
            future = self.producer.send(
                Environment.kafka_topic_ml_recommender_train, key=key, value=message
            )
            future.get(timeout=60)
        self.producer.flush()

    def formatForStreaming(self, model_id, rows):
        messages = []
        max_message_size = 100000
        batch = []
        total = len(rows)
        for row in rows:
            batch.append(
                {
                    "database": self.database,
                    "model_id": model_id,
                    "total": total,
                    "category_id": row["category_id"]
                    if row.get("category_id") is not None
                    else None,
                    "user_id": row["user_id"],
                    "item_id": row["item_id"],
                    "timestamp": row["timestamp"]
                    if row.get("timestamp") is not None
                    else None,
                }
            )
            message_size = len(json.dumps(batch).encode("utf-8"))
            if message_size > max_message_size:
                messages.append(batch)
                batch = []
        messages.append(batch)
        return messages
