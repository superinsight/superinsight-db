import os


class Environment:

    default_storage = os.getenv(
        "ENV_STORAGE", "/db/superinsight/models/private/semantic-search"
    )
    logger_name = os.getenv("ENV_LOGGER_NAME", "SEARCH_LOGS")
    kafka_topic_to_consume = str(os.getenv("ENV_KAFKA_TOPIC_TO_CONSUME", "none"))
    kafka_topic_divide = str(os.getenv("ENV_KAFKA_TOPIC_DIVIDE", "ml_search_divide"))
    kafka_topic_conquer = str(os.getenv("ENV_KAFKA_TOPIC_CONQUER", "ml_search_conquer"))
    kafka_topic_combine = str(
        os.getenv("ENV_KAFKA_TOPIC_TO_COMBINE", "ml_search_combine")
    )
    kafka_topic_conquer_partitions = int(
        os.getenv("ENV_KAFKA_TOPIC_CONQUER_PARTITIONS", "10")
    )
    kafka_topic_combine_partitions = int(
        os.getenv("ENV_KAFKA_TOPIC_COMBINE_PARTITIONS", "5")
    )
    kafka_bootstrap_servers = str(
        os.getenv("ENV_KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    )
    kafka_group_default = str(os.getenv("ENV_KAFKA_GROUP_DEFAULT", "v30"))
    kafka_group_id_local_disk = str(
        os.getenv("ENV_KAFKA_GROUP_ID_LOCAL_DISK", "network-drive")
    )
    semantic_search_model = os.getenv(
        "ENV_SEMANTIC_SEARCH_MODEL",
        "sentence-transformers/distiluse-base-multilingual-cased-v2",
    )
    host_ml_inference = os.getenv(
        "ENV_SUPERINSIGHT_PREDICT_TRANSFORMERS_URL", "http://localhost:8084"
    )
    image_classification_model = os.getenv(
        "ENV_IMAGE_CLASSIFICAION_MODEL", "google/vit-large-patch32-384"
    )
    image_to_text_model = os.getenv(
        "ENV_IMAGE_TO_TEXT_MODEL", "nlpconnect/vit-gpt2-image-captioning"
    )
    s3_access_key = str(os.getenv("AWS_ACCESS_KEY_ID", None))
    s3_secret_key = str(os.getenv("AWS_SECRET_ACCESS_KEY", None))
    index_image_to_caption = os.getenv("ENV_IMAGE_TO_CAPTION", "False") == "True"
    index_image_to_label = os.getenv("ENV_IMAGE_TO_LABEL", "False") == "True"
