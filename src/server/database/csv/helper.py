import logging
import csv

class CsvHelper:

  logger = None

  def __init__(self, logger=None, handler = None):
    self.logger = logger or logging.getLogger(__name__)
    self.logger.setLevel(logging.INFO)
    if handler is not None:
      self.logger.addHandler(handler)
    self.logger.info("Init Database.CSV.CsvHelper...")

  def __del__(self):
    self.logger.info("Exit Database.CSV.CsvHelper...")

  def save(self, dict_list, dest):
    keys = dict_list[0].keys()
    with open(dest, 'w', newline='') as output_file:
      dict_writer = csv.DictWriter(output_file, keys, quoting=csv.QUOTE_NONNUMERIC)
      dict_writer.writeheader()
      dict_writer.writerows(dict_list)
