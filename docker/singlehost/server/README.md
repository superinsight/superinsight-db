## Docker Image for the singlehost-server version of Superinsight

### To build this image run the following command from the root directory
```
docker build -t superinsight/superinsight-db-singlehost-server:latest -f docker/singlehost/server/Dockerfile .
```

### To run the newly build image 
```
docker run --name superinsight-db-singlehost-server -p 5432:5432 -e SUPERINSIGHT_USER=admin -e SUPERINSIGHT_PASSWORD=password superinsight/superinsight-db-singlehost-server:latest
```

### Tag Docker Image
```
docker tag superinsight/superinsight-db-singlehost-server:latest superinsight/superinsight-db-singlehost-server:x.x.x
docker push superinsight/superinsight-db-singlehost-server:x.x.x
```