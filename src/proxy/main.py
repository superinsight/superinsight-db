import importlib, yaml, os
import logging
import time
import traceback
from database.sql.helper import SqlHelper
from postgres_proxy import config_schema as cfg
from postgres_proxy.proxy import Proxy
from environment import Environment

run_as = os.getenv("ENV_RUN_AS", "SERVER")
os.environ["KMP_DUPLICATE_LIB_OK"]="True"
LOG = logging.getLogger(__name__)
version = "0.9.1"

def getConfig():
    path = os.path.dirname(os.path.realpath(__file__))
    config = None
    try:
        with open(path + "/" + "config.yml", "r") as fp:
            config = cfg.Config(yaml.load(fp, Loader=yaml.CLoader))
    except Exception:
        logging.critical("Could not read config. Aborting.")
        exit(1)
    finally:
        return config
    
def startProxyServer():
    config = getConfig()
    qlog = logging.getLogger("intercept")
    qformat = logging.Formatter('%(asctime)s : %(message)s')
    qhandler = logging.FileHandler(config.settings.intercept_log, mode = "w")
    qhandler.setFormatter(qformat)
    qlog.addHandler(qhandler)
    qlog.setLevel(logging.DEBUG)

    print("Starting proxy version {}".format(version))
    print("general log, level {}: {}".format(config.settings.log_level, config.settings.general_log))
    print("intercept log: {}".format(config.settings.intercept_log))
    print("further messages directed to log")

    plugins = {}
    for plugin in config.plugins:
        logging.info("Loading module %s", plugin)
        module = importlib.import_module("plugins." + plugin)
        plugins[plugin] = module

    for instance in config.instances:
        logging.info("Starting proxy instance")
        proxy = Proxy(instance, plugins)
        proxy.listen()  

def serverIsAvailable():
    config = getConfig()
    return SqlHelper().isAvailable(user = Environment.postgres_user, password = Environment.postgres_password , host = config.instances[0].redirect.host, port = config.instances[0].redirect.port, database = Environment.postgres_database)

def setupServer():
    config = getConfig()
    path = os.path.dirname(os.path.realpath(__file__))
    f = open(path + "/" + "setup.sql", "r")
    setup_sql = f.read()
    drop_default_sql = "DROP DATABASE IF EXISTS postgres;"
    SqlHelper().execute(user = Environment.postgres_user, password = Environment.postgres_password , host = config.instances[0].redirect.host, port = config.instances[0].redirect.port, database = Environment.postgres_database, sql= setup_sql)
    SqlHelper().execute(user = Environment.postgres_user, password = Environment.postgres_password , host = config.instances[0].redirect.host, port = config.instances[0].redirect.port, database = Environment.postgres_database, sql= drop_default_sql)
    return True

if(__name__=="__main__"):
    try:
        while serverIsAvailable() is False:
            print("Attempting to connect to server....")
            time.sleep(1)
        setupServer()
        startProxyServer()
    except Exception as e:
        logging.error(traceback.format_exc())