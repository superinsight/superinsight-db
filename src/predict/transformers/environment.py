import os


class Environment:

    logger_name = os.getenv("ENV_LOGGER_NAME", "PREDICT_TRANSFORMERS_LOGS")
    s3_access_key = str(os.getenv("AWS_ACCESS_KEY_ID", None))
    s3_secret_key = str(os.getenv("AWS_SECRET_ACCESS_KEY", None))
    speaker_diarization_model = str(
        os.getenv("SPEAKER_DIARIZATION_MODEL", "pyannote/speaker-diarization@2.1")
    )
    hf_use_auth_token = str(os.getenv("HF_USE_AUTH_TOKEN", None))
