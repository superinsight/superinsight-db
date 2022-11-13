# superinsight-db-server
Machine Learning Database Server
Superinsight Machine Learning Database is SQL/ML Database that uses Postgres SQL as SQL and HuggingFace for Machine Learning

## Installation
```
./setup.sh
```

## Setup
- Make sure you have a running PostgreSQL running
- Setup config.yml 

## Activate the virtual environment
```
source .venv/bin/activate
```

## Run the web server
```
export POSTGRES_HOST="localhost" PGPORT="8432" SUPERINSIGHT_USER="system_admin" SUPERINSIGHT_PASSWORD="password" POSTGRES_DB="superinsight"
uvicorn app:app --host 0.0.0.0 --port 8081 --reload
```

## Run the server as exporter
```
ENV_RUN_AS="EXPORTER" POSTGRES_HOST="localhost" PGPORT="8432" SUPERINSIGHT_USER="system_admin" SUPERINSIGHT_PASSWORD="password" POSTGRES_DB="superinsight" python main.py
```


### Build Docker Image
```
docker build -t superinsight/superinsight-db-server:latest .
```

### Tag Docker Image
```
docker tag superinsight/superinsight-db-server:latest superinsight/superinsight-db-server:x.x.x
docker push superinsight/superinsight-db-server:x.x.x
```

### Run with Docker
```
docker run -d -p 8432:8432 --name superinsight-db-server superinsight/superinsight-db-server:latest
```