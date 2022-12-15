from logging import config
from environment import Environment
from database.consumer import DatabaseConsumer
from database.queue import DatabaseQueue
from common.storage_location import StorageLocation
from common.consume_topic import ConsumeTopic
import time
storage = Environment.default_storage
default_storage = StorageLocation.LOCAL_DISK
version = "0.9.2"
def main():
    if Environment.kafka_topic_to_consume.upper() == ConsumeTopic.DIVIDE.value:
        DatabaseConsumer().consume(topics=Environment.kafka_topic_divide,
                                 storage_location=StorageLocation.LOCAL_DISK)
    if Environment.kafka_topic_to_consume.upper() == ConsumeTopic.CONQUER.value:
        DatabaseConsumer().consume(topics=Environment.kafka_topic_conquer,
                                 storage_location=StorageLocation.LOCAL_DISK)
    if Environment.kafka_topic_to_consume.upper() == ConsumeTopic.COMBINE.value:
        DatabaseConsumer().consume(topics=Environment.kafka_topic_combine,
                                 storage_location=StorageLocation.LOCAL_DISK)
    if Environment.kafka_topic_to_consume.upper() == ConsumeTopic.ALL.value:
        topics = [Environment.kafka_topic_divide, Environment.kafka_topic_conquer, Environment.kafka_topic_combine]
        DatabaseConsumer().consume(topics=topics,
                                   storage_location=StorageLocation.LOCAL_DISK)
    if Environment.kafka_topic_to_consume.upper() == ConsumeTopic.NONE.value:
        while True:
            try:
                DatabaseQueue().dequeue(storage_location=default_storage)
                time.sleep(3)
            except Exception as e:
                print(e)
                time.sleep(30)

if __name__ == "__main__":
    main()
