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
uvicorn app:app --host 0.0.0.0 --port 8082 --reload
```

## Run the server as indexer 
```
ENV_STORAGE="./db" ENV_KAFKA_TOPIC_TO_CONSUME="all" python main.py
ENV_STORAGE="./db" ENV_KAFKA_TOPIC_TO_CONSUME="divide" python main.py
ENV_STORAGE="./db" ENV_KAFKA_TOPIC_TO_CONSUME="conquer" python main.py
ENV_STORAGE="./db" ENV_KAFKA_TOPIC_TO_CONSUME="combine" python main.py
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