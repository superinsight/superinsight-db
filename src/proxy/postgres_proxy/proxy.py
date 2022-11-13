'''For every configured instance, a Proxy object is created, that starts a listener.
On connect, it initiates a parallel connection to postgresql and pairs them together.
Using selectors, packets are received, intercepted and relayed to the other party.

Protocol:
The challenge is in identifying 3 types of packets:
1. With type and data.
   ex. 1 byte for type identifier, 4 bytes header for header and body length, body. Usually the body is ended with
   0x00 byte as well, that is part of the length.
   The queries are part of this type of packets. A query is b'Q####SELECT whatever\\x00'
2. Without type. They contain just a 4 byte header with packet length. It just so happens that the first byte is 0x00
   just because nothing is that long. These contain information about connection.
   Usually it's the client sending connection information. Ex.
        b'x00x00x00O' - length
        b'x00x03x00x00' - unexplained
        then, separated by x00 is a list of key, value: user, database, application_name, client_encoding, etc
        then, ended by b'x00'
3. Without data. Just the type. Since it's b'N', it might be "null"? The whole packet is this single byte.
   Signals "ok" according to wireshark

Handling:
proxy.py - connections and sockets things
connection.py - parsing and composing packets, launching interceptors
interceptors.py - intercepting for modification
'''

import logging
import selectors
import socket
import types
from postgres_proxy import connection, config_schema as cfg
from postgres_proxy.interceptors import ResponseInterceptor, CommandInterceptor

LOG = logging.getLogger(__name__)


class Proxy(object):

    def __init__(self, instance_config, plugins):
        self.plugins = plugins
        self.num_clients = 0
        self.instance_config = instance_config
        self.connections = []
        self.selector = selectors.DefaultSelector()
        self.running = True

    def __create_pg_connection(self, address, context):
        redirect_config = self.instance_config.redirect

        pg_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        pg_sock.connect((redirect_config.host, redirect_config.port))
        pg_sock.setblocking(False)

        events = selectors.EVENT_READ | selectors.EVENT_WRITE

        pg_conn = connection.Connection(pg_sock,
                                        name    = redirect_config.name + '_' + str(self.num_clients),
                                        address = address,
                                        events  = events,
                                        context = context)

        LOG.info("initiated client connection to %s:%s called %s",
                 redirect_config.host, redirect_config.port, redirect_config.name)
        return pg_conn

    def __register_conn(self, conn):
        try:
            self.selector.register(conn.sock, conn.events, data=conn)
        except Exception:
            # potentially already registered - this can happen if file descriptors
            # are reused for new sockets -> try to unregister/re-register
            self.selector.unregister(conn.sock)
            self.selector.register(conn.sock, conn.events, data=conn)

    def __unregister_conn(self, conn):
        self.selector.unregister(conn.sock)

    def accept_wrapper(self, sock):
        clientsocket, address = sock.accept()  # Should be ready to
        clientsocket.setblocking(False)
        self.num_clients+=1
        sock_name = '{}_{}'.format(self.instance_config.listen.name, self.num_clients)
        LOG.info("connection from %s, connection initiated %s", address, sock_name)

        events = selectors.EVENT_READ | selectors.EVENT_WRITE

        # Context dictionary, for sharing state data, connection details, which might be useful for interceptors
        context = {
            'instance_config': self.instance_config
        }

        conn = connection.Connection(clientsocket,
                                     name    = sock_name,
                                     address = address,
                                     events  = events,
                                     context = context)

        pg_conn = self.__create_pg_connection(address, context)

        if self.instance_config.intercept is not None and self.instance_config.intercept.responses is not None:
            pg_conn.interceptor = ResponseInterceptor(self.instance_config.intercept.responses, self.plugins, context)
            pg_conn.redirect_conn = conn

        if self.instance_config.intercept is not None and self.instance_config.intercept.commands is not None:
            conn.interceptor = CommandInterceptor(self.instance_config.intercept.commands, self.plugins, context)
            conn.redirect_conn = pg_conn

        self.__register_conn(conn)
        self.__register_conn(pg_conn)

    def service_connection(self, key, mask):
        sock = key.fileobj
        conn = key.data
        if mask & selectors.EVENT_READ:
            LOG.debug('%s can receive', conn.name)
            recv_data = sock.recv(4096)  # Should be ready to read
            if recv_data:
                LOG.debug('%s received data:\n%s', conn.name, recv_data)
                conn.received(recv_data)
            else:
                LOG.info('%s connection closing %s', conn.name, conn.address)
                sock.close()
        if mask & selectors.EVENT_WRITE:
            if conn.out_bytes:
                LOG.debug('sending to %s:\n%s', conn.name, conn.out_bytes)
                sent = sock.send(conn.out_bytes)  # Should be ready to write
                conn.sent(sent)

    def listen(self, max_connections = 8):
        '''Listen server socket. On connect launch a new thread with the client connection as an argument
        '''
        lconf = self.instance_config.listen
        ip, port = (lconf.host, lconf.port)
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.bind((ip, port))
            self.sock.listen(max_connections)
            self.sock.setblocking(False)
            self.selector.register(self.sock, selectors.EVENT_READ, data=None)
            while self.running:
                events = self.selector.select(timeout=1)
                if not events:
                    continue
                hit = False
                for key, mask in events:
                    hit = True
                    if key.data is None:
                        self.accept_wrapper(key.fileobj)
                    else:
                        self.service_connection(key, mask)
        except OSError as ex:
            LOG.error("Can't establish PostgreSQL proxy listener on port %s" % port, exc_info=ex)
        finally:
            LOG.info("Closing PostgreSQL proxy on port %s" % port)
            self.sock.close()
            self.sock = None

    def stop(self):
        self.running = False