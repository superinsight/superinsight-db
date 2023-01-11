# SuperInsight Inference API

This is a RESTful API that you can use inference public or private models base on the hugging face library, support CPU or GPU

## Environment Variables

| Variable                       | Usage                                                                                 | Required | Default  |
| ------------------------------ | ------------------------------------------------------------------------------------- | -------- | -------- |
| GOOGLE_APPLICATION_CREDENTIALS | If you like to export models to GCP bucket, you will need to include your credentials | False    | None     |
| LOCAL_MODEL_REPOSITORY         | Path used to download and inference finetuned models                                  | False    | ./models |

# Development

## What you will need

- Python 3 installed

## Technologies

- Python 3
- HuggingFace
- FastAPI

## Installation virtual environment

```
python3 -m pip install virtualenv
python3 -m virtualenv -p python3 .venv
```

## Activate the virtual environment

```
source .venv/bin/activate
```

## Install Dependencies and run API

```
pip install -r requirements.txt
export AWS_ACCESS_KEY_ID=xxxx
export AWS_SECRET_ACCESS_KEY=xxxxx
```

```
export $(xargs < .env)
uvicorn app:app --host 0.0.0.0 --port 8084 --reload
```
