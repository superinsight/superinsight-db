from environment import Environment
from database.consumer import DatabaseConsumer
from database.queue import DatabaseQueue
from common.storage_location import StorageLocation
from common.consume_topic import ConsumeTopic
from common.logger import CommonLogger
from database.kafka_admin import DatabaseKafkaAdmin
import time

storage = Environment.default_storage
default_storage = StorageLocation.LOCAL_DISK
logger = CommonLogger()


def main():
    logger.info("Main...")
    logger.info("Consuming starting...", Environment.kafka_topic_to_consume.upper())
    try:
        if Environment.kafka_topic_to_consume.upper() == ConsumeTopic.DIVIDE.value:
            DatabaseKafkaAdmin.create_topic(Environment.kafka_topic_divide)
            DatabaseConsumer().consume(
                topics=Environment.kafka_topic_divide,
                storage_location=StorageLocation.LOCAL_DISK,
            )
        if Environment.kafka_topic_to_consume.upper() == ConsumeTopic.CONQUER.value:
            DatabaseKafkaAdmin.create_topic(Environment.kafka_topic_conquer)
            DatabaseConsumer().consume(
                topics=Environment.kafka_topic_conquer,
                storage_location=StorageLocation.LOCAL_DISK,
            )
        if Environment.kafka_topic_to_consume.upper() == ConsumeTopic.COMBINE.value:
            DatabaseKafkaAdmin.create_topic(Environment.kafka_topic_combine)
            DatabaseConsumer().consume(
                topics=Environment.kafka_topic_combine,
                storage_location=StorageLocation.LOCAL_DISK,
            )
        if Environment.kafka_topic_to_consume.upper() == ConsumeTopic.ALL.value:
            topics = [
                Environment.kafka_topic_divide,
                Environment.kafka_topic_conquer,
                Environment.kafka_topic_combine,
            ]
            DatabaseKafkaAdmin.create_topic(Environment.kafka_topic_divide)
            DatabaseKafkaAdmin.create_topic(
                Environment.kafka_topic_conquer,
                Environment.kafka_topic_conquer_partitions,
            )
            DatabaseKafkaAdmin.create_topic(
                Environment.kafka_topic_combine,
                Environment.kafka_topic_combine_partitions,
            )
            DatabaseConsumer().consume(
                topics=topics, storage_location=StorageLocation.LOCAL_DISK
            )
        if Environment.kafka_topic_to_consume.upper() == ConsumeTopic.NONE.value:
            while True:
                try:
                    DatabaseQueue().dequeue(storage_location=default_storage)
                    time.sleep(3)
                except Exception as e:
                    logger.error(e)
                    time.sleep(30)
    except Exception as e:
        logger.error(e)


if __name__ == "__main__":
    main()
