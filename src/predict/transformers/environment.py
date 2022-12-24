import os


class Environment:

    logger_name = os.getenv("ENV_LOGGER_NAME", "PREDICT_TRANSFORMERS_LOGS")
    s3_access_key = str(os.getenv("AWS_ACCESS_KEY_ID", None))
    s3_secret_key = str(os.getenv("AWS_SECRET_ACCESS_KEY", None))
