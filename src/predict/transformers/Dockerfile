FROM python:3.8
ADD ./ /inference
WORKDIR /inference
RUN apt-get -y update
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
ENV PYTHONUNBUFFERED=1
RUN pip install -r requirements.txt 
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]