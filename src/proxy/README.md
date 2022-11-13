# superinsight-db-proxy
Proxy For Machine Learning Database Server
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

## Run the server as proxy
```
POSTGRES_DB=superinsight SUPERINSIGHT_USER=admin SUPERINSIGHT_PASSWORD=password ENV_HOST_MLDB="http://127.0.0.1:8081" python main.py
```

### Run with Docker
```
docker run -d --env ENV_REDIRECT_PORT=xxxxxxx --env ENV_REDIRECT_HOST=xxxxxxx -p 8432:8432 --name superinsight-db-proxy superinsight/superinsight-db-proxy:latest
```

### Build Docker Image
```
docker build -t superinsight/superinsight-db-proxy:latest .
```

### Tag Docker Image
```
docker tag superinsight/superinsight-db-proxy:latest superinsight/superinsight-db-proxy:x.x.x
docker push superinsight/superinsight-db-proxy:x.x.x
```