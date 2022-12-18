from kafka import KafkaAdminClient
from kafka import KafkaConsumer
from kafka.admin import NewTopic
from environment import Environment
from common.logger import CommonLogger


class DatabaseKafkaAdmin:
    def create_topic(topic, num_of_partitions=1):
        logger = CommonLogger()
        topics = KafkaConsumer(
            bootstrap_servers=Environment.kafka_bootstrap_servers
        ).topics()
        if topic in topics:
            logger.info(
                "DatabaseKafkaAdmin.create_topic:topic", topic, "already exists"
            )
            return True
        admin_client = KafkaAdminClient(
            bootstrap_servers=Environment.kafka_bootstrap_servers
        )
        topic_list = []
        topic_list.append(
            NewTopic(name=topic, num_partitions=num_of_partitions, replication_factor=1)
        )
        logger.info("DatabaseKafkaAdmin.create_topic:topic")
        admin_client.create_topics(new_topics=topic_list, validate_only=False)
