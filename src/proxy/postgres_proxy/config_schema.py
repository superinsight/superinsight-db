import logging

''' This class is used to validate the config
'''
class Schema:
    def __init__(self):
        pass

    def _validate(self):
        pass

    def __hyphen_to_underscore(self, k):
        return k.replace('-', '_')

    def _populate(self, data, definition):
        try:
            for (k, v) in data.items():
                k = self.__hyphen_to_underscore(k)
                if k in definition:
                    vtype = definition[k]
                    if isinstance(vtype, list):
                        assert isinstance(v, list), "{} should be a list".format(k)
                        newlist = []
                        for item in v:
                            newlist.append(vtype[0](item))
                        setattr(self, k, newlist)
                    else:
                        setattr(self, k, vtype(v))
            self._validate()
        except AssertionError as err:
            logging.error("Invalid config: %s", str(err))
            raise Exception("Invalid config")

    def _assert_non_empty(self, *attrs):
        for attr in attrs:
            assert len(getattr(self, attr)) > 0, "{}.{} must not be empty".format(type(self).__name__, attr)

    def _assert_non_null(self, *attrs):
        for attr in attrs:
            assert getattr(self, attr) is not None, "{}.{} must not be None".format(type(self).__name__, attr)


class InterceptQuerySettings(Schema):
    def __init__(self, data):
        self.plugin = None
        self.function = None

        self._populate(data, {
            'plugin': str,
            'function': str
        })

    def _validate(self):
        self._assert_non_null('plugin', 'function')
        self._assert_non_empty('plugin', 'function')


class InterceptCommandSettings(Schema):
    def __init__(self, data):
        self.queries = []
        self.connects = None

        self._populate(data, {
            'queries': [InterceptQuerySettings],
            'connects': str
        })


class InterceptSettings(Schema):
    def __init__(self, data):
        self.commands = None
        self.responses = None

        self._populate(data, {
            'commands': InterceptCommandSettings,
            'responses': str
        })


class Connection(Schema):
    def __init__(self, data):
        self.name = None
        self.host = None
        self.port = None

        self._populate(data, {
            'name': str,
            'host': str,
            'port': int
        })

    def _validate(self):
        self._assert_non_null('name', 'host', 'port')
        self._assert_non_empty('name')


class InstanceSettings(Schema):
    def __init__(self, data):
        self.listen = None
        self.redirect = None
        self.intercept = None

        self._populate(data, {
            'listen': Connection,
            'redirect': Connection,
            'intercept': InterceptSettings
        })


    def _validate(self):
        self._assert_non_null('listen', 'redirect')


class Settings(Schema):
    def __init__(self, data):
        self.log_level = None
        self.intercept_log = None
        self.general_log = None

        self._populate(data, {
            'log_level': str,
            'intercept_log': str,
            'general_log': str
        })

    def _validate(self):
        self._assert_non_null('log_level', 'intercept_log', 'general_log')
        self._assert_non_empty('log_level', 'intercept_log', 'general_log')


class Config(Schema):
    def __init__(self, data):
        self.plugins = []
        self.settings = None
        self.instances = []

        self._populate(data, {
            'plugins' : [str],
            'settings' : Settings,
            'instances' : [InstanceSettings]
        })

    def _validate(self):
        self._assert_non_empty('instances')
