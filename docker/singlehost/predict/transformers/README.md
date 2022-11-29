## Docker Image for the singlehost-server version of Superinsight

### To build this image run the following command from the root directory
```
docker build -t superinsight/superinsight-db-singlehost-predict-transformers:latest -f docker/singlehost/predict/transformers/Dockerfile .
```

### To run the newly build image 
```
docker run --name superinsight-db-singlehost-predict-transformers superinsight/superinsight-db-singlehost-predict-transformers:latest
```

### Tag Docker Image
```
docker tag superinsight/superinsight-db-singlehost-predict-transformers:latest superinsight/superinsight-db-singlehost-predict-transformers:x.x.x
docker push superinsight/superinsight-db-singlehost-predict-transformers:x.x.x
```