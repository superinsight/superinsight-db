if [[ $ENV_RUN_AS = "WEBSERVER" ]]
then
    echo "starting webserver..."
    if [ ! -d "models" ] ; then
        mkdir models
    fi
    uvicorn app:app --host 0.0.0.0 --port 8080 --reload --log-config log-config.json
fi
if [[ $ENV_RUN_AS = "EXPORTER" ]]
then
    echo "starting exporter..."
    python3 main.py
fi