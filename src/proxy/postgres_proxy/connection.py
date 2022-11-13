import logging

_logger = logging.getLogger("postgres_proxy")

class Connection:
    def __init__(self, sock, address, name, events, context):
        self.sock = sock
        self.address = address
        self.name = name
        self.events = events
        self.context = context
        self.interceptor = None
        self.redirect_conn = None
        self.out_bytes = b''
        self.in_bytes = b''

    def parse_length(self, length_bytes):
        return int.from_bytes(length_bytes, 'big')

    def encode_length(self, length):
        return length.to_bytes(4, byteorder='big')

    def received(self, in_bytes):
        self.in_bytes += in_bytes
        # Read packet from byte array while there are enough bytes to make up a packet.
        # Otherwise wait for more bytes to be received (break and exit)
        while True:
            ptype = self.in_bytes[0:1]
            if ptype == b'\x00':
                if len(self.in_bytes) < 4:
                    break
                header_length = 4
                body_length = self.parse_length(self.in_bytes[0:4]) - 4
            elif ptype == b'N':
                header_length = 1
                body_length = 0
            else:
                if len(self.in_bytes) < 5:
                    break
                header_length = 5
                body_length = self.parse_length(self.in_bytes[1:5]) - 4

            length = header_length + body_length
            if len(self.in_bytes) < length:
                break
            header = self.in_bytes[0:header_length]
            body = self.in_bytes[header_length:length]
            self.process_inbound_packet(header, body)
            self.in_bytes = self.in_bytes[length:]

    def process_inbound_packet(self, header, body):
        if header != b'N':
            packet_type = header[0:-4]
            _logger.info("intercepting packet of type '%s' from %s", packet_type, self.name)
            body = self.interceptor.intercept(packet_type, body)
            header = packet_type + self.encode_length(len(body) + 4)

        message = header + body
        _logger.debug("Received message. Relaying. Speaker: %s, message:\n%s", self.name, message)
        self.redirect_conn.out_bytes += message

    def sent(self, num_bytes):
        self.out_bytes = self.out_bytes[num_bytes:]
