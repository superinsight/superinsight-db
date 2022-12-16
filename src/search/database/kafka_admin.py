import logging
from kafka import KafkaAdminClient
from kafka import KafkaConsumer
from kafka.admin import NewTopic
from environment import Environment


class DatabaseKafkaAdmin:

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    def create_topic(topic, num_of_partitions=1):
        topics = KafkaConsumer().topics()
        if topic in topics:
            return True
        admin_client = KafkaAdminClient(
            bootstrap_servers=Environment.kafka_bootstrap_servers
        )
        topic_list = []
        topic_list.append(
            NewTopic(name=topic, num_partitions=num_of_partitions, replication_factor=1)
        )
        admin_client.create_topics(new_topics=topic_list, validate_only=False)
