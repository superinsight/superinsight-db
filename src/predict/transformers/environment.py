import os


class Environment:

    logger_name = os.getenv("ENV_LOGGER_NAME", "PREDICT_TRANSFORMERS_LOGS")
