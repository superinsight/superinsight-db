FROM python:3.8
COPY ./src/predict/transformers /app
WORKDIR /app
RUN apt-get -y update
RUN	apt-get install -y --no-install-recommends \
    libsndfile1 \
    ffmpeg
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
ENV PYTHONUNBUFFERED=1
RUN pip install -r requirements.txt 
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]