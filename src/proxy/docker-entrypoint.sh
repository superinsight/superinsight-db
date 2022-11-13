sed -i -e "s/##instances_redirect_host##/$ENV_REDIRECT_HOST/g" config.yml
sed -i -e "s/##instances_redirect_port##/$ENV_REDIRECT_PORT/g" config.yml
python main.py