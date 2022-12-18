## Run script from root of project
docker build -t superinsight/superinsight-db-singlehost-server:local -f docker/singlehost/server/Dockerfile .
docker build -t superinsight/superinsight-db-singlehost-search:local -f docker/singlehost/search/Dockerfile .
docker build -t superinsight/superinsight-db-singlehost-predict-transformers:local -f docker/singlehost/predict/transformers/Dockerfile .