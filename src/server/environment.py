import os


class Environment:

    app_instance_id = os.getenv("ENV_APP_INSTANCE_ID", "_DB_SERVER")
    logger_name = os.getenv("ENV_LOGGER_NAME", "SERVER_LOGS")
    postgres_database = os.getenv("POSTGRES_DB", "superinsight")
    postgres_user = os.getenv("SUPERINSIGHT_USER", "admin")
    postgres_password = os.getenv("SUPERINSIGHT_PASSWORD", "password")
    postgres_host = os.getenv("POSTGRES_HOST", "localhost")
    postgres_port = os.getenv("PGPORT", "8432")
    table_logs_read_size = int(os.getenv("ENV_TABLE_LOGS_READ_SIZE", "1000"))
    provider_inference_default = os.getenv(
        "ENV_PROVIDER_INFERENCE_DEFAULT", "SUPERINSIGHT"
    )
    default_export_table_interval = int(os.getenv("ENV_ARCHIVER_DISK_INTERVAL", "10"))
    default_model_question_answering = os.getenv(
        "ENV_MODEL_QUESTION_ANSWERING", "deepset/xlm-roberta-large-squad2"
    )
    default_model_summarization = os.getenv(
        "ENV_MODEL_SUMMARIZATION", "facebook/bart-large-cnn"
    )
    default_model_text_classification = os.getenv(
        "ENV_MODEL_TEXT_CLASSIFICATION", "facebook/bart-large-mnli"
    )
    default_model_text_generation = os.getenv(
        "ENV_MODEL_TEXT_GENERATION", "facebook/opt-1.3b"
    )
    default_model_translation = os.getenv(
        "ENV_MODEL_TRANSLATION", "facebook/mbart-large-50-many-to-many-mmt"
    )
    default_model_type_translation = os.getenv("ENV_MODEL_TYPE_TRANSLATION", "mbart")
    provider_api_url_superinsight = os.getenv(
        "ENV_SUPERINSIGHT_PREDICT_TRANSFORMERS_URL", "http://0.0.0.0:8084"
    )
    provider_api_url_superinsight_recommender = os.getenv(
        "ENV_SUPERINSIGHT_RECOMMENDER_URL", "http://localhost:8081"
    )
    provider_api_url_superinsight_search = os.getenv(
        "ENV_SUPERINSIGHT_SEARCH_URL", "http://localhost:8082"
    )
    provider_api_url_superinsight_search_indexing = os.getenv(
        "ENV_SUPERINSIGHT_SEARCH_INDEXING_URL", "http://localhost:8082"
    )
    text_generation_inputs_name = os.getenv("ENV_TEXT_GENERATION_INPUTS_NAME", "inputs")
    question_answering_inputs_name = os.getenv(
        "ENV_QUESTION_ANSWERING_INPUTS_NAME", "inputs"
    )
    summarization_inputs_name = os.getenv("ENV_SUMMARIZATION_INPUTS_NAME", "inputs")
    translation_inputs_name = os.getenv("ENV_TRANSLATION_INPUTS_NAME", "inputs")
    semantic_search_inputs_name = os.getenv("ENV_SEMANTIC_SEARCH_INPUTS_NAME", "inputs")
    recommender_inputs_name = os.getenv("ENV_RECOMMENDER_INPUTS_NAME", "user_id")
    mldb_schema_name = os.getenv("ENV_MLDB_SCHEMA", "mldb")
    model_schema_name = os.getenv("ENV_MODEL_SCHEMA", "model")
    storage_model_private_recommender = os.getenv(
        "ENV_STORAGE_MODEL_PRIVATE_RECOMMENDER",
        "/db/superinsight/models/private/semantic-search",
    )
    kafka_topic_ml_search = str(
        os.getenv("ENV_KAFKA_TOPIC_ML_SEARCH", "ml_search_divide")
    )
    kafka_topic_ml_recommender_train = str(
        os.getenv(
            "ENV_KAFKA_TOPIC_ML_RECOMMENDER_TRAIN",
            "superinsight_ml_recommender_train_v0",
        )
    )
    kafka_bootstrap_servers = str(
        os.getenv("ENV_KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    )
    kafka_enabled = os.getenv("ENV_KAFKA_ENABLED", "False") == "True"
