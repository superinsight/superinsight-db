## Docker Image for the standalone version of Superinsight

### To build this image run the following command from the root directory

```
docker build -t superinsight/superinsight-db-standalone:local -f docker/standalone/Dockerfile .
```

### To run the newly build image

```
docker run --name superinsight-db-standalone -p 5432:5432 -e SUPERINSIGHT_USER=admin -e SUPERINSIGHT_PASSWORD=password superinsight/superinsight-db-standalone:latest
```

### Tag Docker Image

```
docker tag superinsight/superinsight-db-standalone:latest superinsight/superinsight-db-standalone:x.x.x
docker push superinsight/superinsight-db-standalone:x.x.x
```
