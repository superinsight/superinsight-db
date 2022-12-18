import csv
from common.logger import CommonLogger


class CsvHelper:

    logger = None

    def __init__(self, logger=None, handler=None):
        self.logger = CommonLogger(logger=logger, handler=handler)
        self.logger.info("Init Database.CSV.CsvHelper...")

    def __del__(self):
        self.logger.info("Exit Database.CSV.CsvHelper...")

    def save(self, dict_list, dest):
        keys = dict_list[0].keys()
        with open(dest, "w", newline="") as output_file:
            dict_writer = csv.DictWriter(
                output_file, keys, quoting=csv.QUOTE_NONNUMERIC
            )
            dict_writer.writeheader()
            dict_writer.writerows(dict_list)
