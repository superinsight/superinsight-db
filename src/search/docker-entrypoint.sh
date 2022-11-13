if [[ $ENV_RUN_AS = "SEARCH" ]]
then
    echo "starting semantic search web server..."
    uvicorn app:app --host 0.0.0.0 --port 8080 --reload
fi
if [[ $ENV_RUN_AS = "INDEXER" ]]
then
    echo "starting indexer..."
    python3 main.py
fi