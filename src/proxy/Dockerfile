FROM python:3.8
ADD ./ /app
WORKDIR /app
RUN apt-get -y update
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
ENV PYTHONUNBUFFERED=1
RUN pip install -r requirements.txt 
RUN chmod +x ./docker-entrypoint.sh
CMD [ "bash", "./docker-entrypoint.sh" ]