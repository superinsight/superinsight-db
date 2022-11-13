import importlib
import sys

""" Rudimentary test runner for plugins
Pass in the plugin name as an argument, and make sure that there is a test.py file with a run() function in the plugin
directory.
"""

plugin = sys.argv[1]
test = importlib.import_module('plugins.' + plugin + '.test')

test.run()
