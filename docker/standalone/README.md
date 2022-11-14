## Docker Image for the standalone version of Superinsight

### To build this image run the following command from the root directory
```
docker build -t superinsight/superinsight-db-standalone:latest -f docker/standalone/Dockerfile .
```

### Tag Docker Image
```
docker tag superinsight/superinsight-db-standalone:latest superinsight/superinsight-db-standalone:x.x.x
docker push superinsight/superinsight-db-standalone:x.x.x
```