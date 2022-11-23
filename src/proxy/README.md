# superinsight-db-proxy
Proxy For Machine Learning Database Server
Superinsight Machine Learning Database is SQL/ML Database that uses Postgres SQL as SQL and HuggingFace for Machine Learning

## Installation
```
./setup.sh
```

## Activate the virtual environment
```
source .venv/bin/activate
```

## Run the proxy
```
SUPERINSIGHT_USER=admin SUPERINSIGHT_PASSWORD=password ENV_HOST_MLDB="http://127.0.0.1:8081" python main.py
```