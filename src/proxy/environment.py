import os 

class Environment:

  host_mldb = os.getenv("ENV_HOST_MLDB", "http://127.0.0.1:8081") 
  cache_mldb_resp_sec = int(os.getenv("ENV_MLDB_RESP_SEC", "30"))
  mldb_schema_name = os.getenv("ENV_MLDB_SCHEMA", "mldb")
  model_schema_name = os.getenv("ENV_MODEL_SCHEMA", "model")
  postgres_database = os.getenv("POSTGRES_DB", "superinsight")
  postgres_user = os.getenv("SUPERINSIGHT_USER", "admin")
  postgres_password = os.getenv("SUPERINSIGHT_PASSWORD", "password")