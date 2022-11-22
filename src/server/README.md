# superinsight-db-server
Machine Learning Database Server
Superinsight Machine Learning Database is SQL/ML Database that uses Postgres SQL as SQL and HuggingFace for Machine Learning

## Installation
```
./setup.sh
```

## Activate the virtual environment
```
source .venv/bin/activate
```

## Run the web server
```
export POSTGRES_HOST="localhost" PGPORT="8432" SUPERINSIGHT_USER="admin" SUPERINSIGHT_PASSWORD="password" POSTGRES_DB="superinsight"
uvicorn app:app --host 0.0.0.0 --port 8081 --reload
```

## Run the server as exporter
```
ENV_RUN_AS="EXPORTER" POSTGRES_HOST="localhost" PGPORT="8432" SUPERINSIGHT_USER="admin" SUPERINSIGHT_PASSWORD="password" python main.py
```