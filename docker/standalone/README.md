## Docker Image for the standalone version of Superinsight

### To build this image run the following command from the root directory
```
docker build -t superinsight/superinsight-db-standalone:latest -f docker/standalone/Dockerfile .
docker build -t superinsight/superinsight-db-standalone-small:latest -f docker/standalone/Dockerfile .
```
docker run --name superinsight-db-standalone-small -p 5432:5432 -e SUPERINSIGHT_USER=admin -e SUPERINSIGHT_PASSWORD=password superinsight/superinsight-db-standalone-small:latest

### Tag Docker Image
```
docker tag superinsight/superinsight-db-standalone:latest superinsight/superinsight-db-standalone:x.x.x
docker push superinsight/superinsight-db-standalone:x.x.x
```