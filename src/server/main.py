import time
from database.sql.helper import SqlHelper
from environment import Environment
from worker.exporter import Exporter
from common.export_destination import ExportDestination
from common.logger import CommonLogger

logger = CommonLogger()


def serverIsAvailable():
    return SqlHelper(database=Environment.postgres_database).isAvailable()


def main():
    destination = ExportDestination.HTTP
    if Environment.kafka_enabled is True:
        destination = ExportDestination.STREAMING
    exporter = Exporter(
        instance_id=Environment.app_instance_id,
        database=Environment.postgres_database,
        destination=destination,
    )
    while True:
        exporter.exportTableLogger()
        time.sleep(Environment.default_export_table_interval)


if __name__ == "__main__":
    while serverIsAvailable() is False:
        logger.info("Attempting to connect to server....")
        time.sleep(1)
    main()
