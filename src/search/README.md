# superinsight-ml-search
Superinsight Semantic Search System


## Installation virtual environment
```
python3 -m pip install virtualenv
python3 -m virtualenv -p python3 .venv
```

## Activate the virtual environment
```
source .venv/bin/activate
```

## Install dependencies
```
pip install -r requirements.txt
```

## Run the server as search
```
ENV_STORAGE="./db" uvicorn app:app --host 0.0.0.0 --port 8082 --reload
```

## Run the server as indexer if using kafka 
```
ENV_STORAGE="./db" ENV_KAFKA_TOPIC_TO_CONSUME="all" python main.py
ENV_STORAGE="./db" ENV_KAFKA_TOPIC_TO_CONSUME="divide" python main.py
ENV_STORAGE="./db" ENV_KAFKA_TOPIC_TO_CONSUME="conquer" python main.py
ENV_STORAGE="./db" ENV_KAFKA_TOPIC_TO_CONSUME="combine" python main.py
```

## Start Redis Server Locally or with docker if using redis queue
```
docker run --name my-redis-container -p 6379:6379 -d redis
```
```
redis-server
```
```
ENV_STORAGE="./db" rq worker --with-scheduler
```

### Build Docker Image
```
docker build -t superinsight/superinsight-ml-search:latest .
```

### Tag Docker Image
```
docker tag superinsight/superinsight-ml-search:latest superinsight/superinsight-ml-search:x.x.x
docker push superinsight/superinsight-ml-search:x.x.x
```

### Run with Docker
```
docker run -d --name superinsight-ml-search superinsight/superinsight-ml-search:latest
```