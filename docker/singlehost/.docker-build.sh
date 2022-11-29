## Run script from root of project
docker build -t superinsight/superinsight-db-singlehost-server:latest -f docker/singlehost/server/Dockerfile .
docker build -t superinsight/superinsight-db-singlehost-search:latest -f docker/singlehost/search/Dockerfile .
docker build -t superinsight/superinsight-db-singlehost-predict-transformers:latest -f docker/singlehost/predict/transformers/Dockerfile .