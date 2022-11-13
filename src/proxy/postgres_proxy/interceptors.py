import logging
from pg8000.converters import PG_PY_ENCODINGS

from postgres_proxy.constants import ALLOWED_CONNECTION_PARAMETERS


class Interceptor:
    def __init__(self, interceptor_config, plugins, context):
        self.interceptor_config = interceptor_config
        self.plugins = plugins
        self.context = context

    def intercept(self, packet_type, data):
        return data

    def get_codec(self):
        if self.context is not None and 'connect_params' in self.context:
            if self.context['connect_params'] is not None and 'client_encoding' in self.context['connect_params']:
                return self.convert_encoding_to_python(self.context['connect_params']['client_encoding'])
        return 'utf-8'

    @staticmethod
    def convert_encoding_to_python(encoding: str) -> str:
        encoding = encoding.lower()
        result = PG_PY_ENCODINGS.get(encoding, encoding)
        if not result:
            raise Exception(f"Encoding {encoding} not supported by postgresql-proxy!")
        return result


class CommandInterceptor(Interceptor):
    def intercept(self, packet_type, data):
        if self.interceptor_config.queries is not None:
            ic_queries = self.interceptor_config.queries
            if packet_type == b'Q':
                # Query, ends with b'\x00'
                data = self.__intercept_query(data, ic_queries)
            elif packet_type == b'P':
                # Statement that needs parsing.
                # First byte of the body is some Statement flag. Ignore, don't lose
                # Next is the query, same as above, ends with an b'\x00'
                # Last 2 bytes are the number of parameters. Ignore, don't lose
                statement = data[0:1]
                query = self.__intercept_query(data[1:-2], ic_queries)
                params = data[-2:]
                data = statement + query + params
            elif packet_type == b'':
                # Connection request / context. Ignore the first 4 bytes, keep it
                packet_start = data[0:4]
                context_data = self.__intercept_context_data(data[4:-1])
                data = packet_start + context_data
        return data

    def __intercept_context_data(self, data):
        # Each entry is terminated by b'\x00'
        entries = data.split(b'\x00')[:-1]
        entries = dict(zip(entries[0::2], entries[1::2]))
        self.context['connect_params'] = {}
        # Try to set codec, then transcode the dict
        if b'client_encoding' in entries:
            self.context['connect_params']['client_encoding'] = entries[b'client_encoding'].decode('ascii')
        codec = self.get_codec()
        for k, v in entries.items():
            key: str = k.decode(codec)
            # don't keep parameters not allowed by postgres
            if key.lower() not in ALLOWED_CONNECTION_PARAMETERS:
                continue
            self.context['connect_params'][k.decode(codec)] = v.decode(codec)

        context_data = b'\x00'.join(
            [
                key.encode(codec) + b'\x00' + value.encode(codec)
                for key, value in self.context['connect_params'].items()
            ]
        )
        return context_data + b'\x00\x00'

    def __intercept_query(self, query, interceptors):
        try:
            orignal_query = query
            logging.getLogger('intercept').debug("intercepting query\n%s", query)
            # Remove zero byte at the end
            query = query[:-1].decode('utf-8')
            for interceptor in interceptors:
                if interceptor.plugin in self.plugins:
                    plugin = self.plugins[interceptor.plugin]
                    if hasattr(plugin, interceptor.function):
                        func = getattr(plugin, interceptor.function)
                        query = func(query, self.context)
                        logging.getLogger('intercept').debug(
                            "modifying query using interceptor %s.%s\n%s",
                            interceptor.plugin,
                            interceptor.function,
                            query)
                    else:
                        raise Exception("Can't find function {} in plugin {}".format(
                            interceptor.function,
                            interceptor.plugin
                        ))
                else:
                    raise Exception("Plugin {} not loaded".format(interceptor.plugin))
            # Append the zero byte at the end
            return query.encode('utf-8') + b'\x00'
        except:
            return orignal_query

class ResponseInterceptor(Interceptor):
    pass
