## Docker Image for the singlehost-server version of Superinsight

### To build this image run the following command from the root directory
```
docker build -t superinsight/superinsight-db-singlehost-search:latest -f docker/singlehost/search/Dockerfile .
```

### To run the newly build image 
```
docker run --name superinsight-db-singlehost-search -e ENV_RUN_AS=SEARCH superinsight/superinsight-db-singlehost-search:latest
docker run --name superinsight-db-singlehost-search -e ENV_RUN_AS=INDEXER superinsight/superinsight-db-singlehost-search:latest
```

### Tag Docker Image
```
docker tag superinsight/superinsight-db-singlehost-search:latest superinsight/superinsight-db-singlehost-search:x.x.x
docker push superinsight/superinsight-db-singlehost-search:x.x.x
```