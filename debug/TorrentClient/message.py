from struct import pack, unpack
from queue import Queue


class MessageQueue(Queue):
    def __init__(self):
        Queue.__init__(self)
        self.length = None

    def get_message(self):
        ''' Return the message at the front of the queue, or None if
        if there is not a complete message. '''
        length = self.peek_length()
        if length is not None and length + 4 <= self.qsize():
            msg = bytearray()
            for _ in range(length + 4):
                msg.append(self.get())
            return Message.get_message_from_bytes(msg)
        else:
            return None

    def peek_length(self):
        ''' Return the length of the message at the front of the queue.
        Useful when determining if a full message can be pulled.'''
        if self.qsize() < 4:
            return None
        length = bytes([self.queue[0],
                        self.queue[1],
                        self.queue[2],
                        self.queue[3]])
        return unpack('>L', length)[0]


class Message(object):

    def __init__(self):
        self.length = None
        self.id = None
        self.payload = None
        self.begin = None
        self.length = None
        self.block = None
        self.port = None
        self.bitfield = None

    # Factory method for generating message objects
    @staticmethod
    def get_message(msg_type,
                    index=None,
                    begin=None,
                    length=None,
                    block=None,
                    port=None,
                    bitfield=None):
        if msg_type == 'keep-alive':
            return KeepAlive()
        elif msg_type == 'choke':
            return Choke()
        elif msg_type == 'unchoke':
            return UnChoke()
        elif msg_type == 'interested':
            return Interested()
        elif msg_type == 'not interested':
            return NotInterested()
        elif msg_type == 'have':
            return Have(index)
        elif msg_type == 'bitfield':
            return BitField(bitfield)
        elif msg_type == 'request':
            return Request(index, begin, length)
        elif msg_type == 'piece':
            return Piece(index, begin, block)
        elif msg_type == 'cancel':
            return Cancel(index, begin, length)
        elif msg_type == 'port':
            return Port(port)
        else:
            raise ValueError('Unknown message type %s' % msg_type)

    # Factory method for generating message objects from raw bytes
    @staticmethod
    def get_message_from_bytes(payload):
        length = unpack('!l', payload[:4])[0]

        # go ahead and handle the KeepAlive first
        if length == 0:
            return KeepAlive()

        # make sure the length is actually correct before parsing
        # if length != len(payload) - 4:
        #     raise Exception('Message length mismatch')

        # get the id and start parsing
        msg_id = int(unpack('!c', payload[4:5])[0][0])
        if msg_id == 0:
            return Choke()
        elif msg_id == 1:
            return UnChoke()
        elif msg_id == 2:
            return Interested()
        elif msg_id == 3:
            return NotInterested()
        elif msg_id == 4:
            index = unpack('!l', payload[5:])[0]
            return Have(index)
        elif msg_id == 5:
            bitfield = payload[5:]
            return BitField(bitfield)
        elif msg_id == 6:
            index = int(unpack('!l', payload[5:9])[0])
            begin = int(unpack('!l', payload[9:13])[0])
            r_length = int(unpack('!l', payload[13:])[0])
            return Request(index, begin, r_length)
        elif msg_id == 7:
            index = int(unpack('!l', payload[5:9])[0])
            begin = int(unpack('!l', payload[9:13])[0])
            block = payload[13:]
            return Piece(index, begin, block)
        elif msg_id == 8:
            index = int(unpack('!l', payload[5:9])[0])
            begin = int(unpack('!l', payload[9:13])[0])
            r_length = int(unpack('!l', payload[13:])[0])
            return Cancel(index, begin, r_length)
        elif msg_id == 9:
            port = int(unpack('!H', payload[5:])[0])
            return Port(port)
        else:
            raise Exception('Unknown message id %s' % msg_id)

    def to_bytes(self):
        if self.length is not None:
            r = pack('!l', self.length)
        if self.id is not None:
            r += pack('!c', bytes([self.id]))
        return r

    def __eq__(self, other):
        return self.to_bytes() == other.to_bytes()


class KeepAlive(Message):
    '''keep-alive: <len=0000>

    The keep-alive message is a message with zero bytes, specified with
    the length prefix set to zero. There is no message ID and no
    payload. Peers may close a connection if they receive no messages
    (keep-alive or any other message) for a certain period of time, so a
    keep-alive message must be sent to maintain the connection alive if
    no command have been sent for a given amount of time. This amount of
    time is generally two minutes.
    '''
    def __init__(self):
        Message.__init__(self)
        self.length = 0


class Choke(Message):
    '''choke: <len=0001><id=0>

    The choke message is fixed-length and has no payload.
    '''
    def __init__(self):
        Message.__init__(self)
        self.length = 1
        self.id = 0


class UnChoke(Message):
    '''unchoke: <len=0001><id=1>

    The unchoke message is fixed-length and has no payload.
    '''
    def __init__(self):
        Message.__init__(self)
        self.length = 1
        self.id = 1


class Interested(Message):
    '''interested: <len=0001><id=2>

    The interested message is fixed-length and has no payload.
    '''
    def __init__(self):
        Message.__init__(self)
        self.length = 1
        self.id = 2


class NotInterested(Message):
    '''not interested: <len=0001><id=3>

    The not interested message is fixed-length and has no payload.
    '''
    def __init__(self):
        Message.__init__(self)
        self.length = 1
        self.id = 3


class Have(Message):
    '''have: <len=0005><id=4><piece index>

    The have message is fixed length. The payload is the zero-based
    index of a piece that has just been successfully downloaded and
    verified via the hash.
    '''
    def __init__(self, index):
        self.length = 5
        self.id = 4
        self.index = index

    def to_bytes(self):
        return super(Have, self).to_bytes() + pack('!l', self.index)


class BitField(Message):
    '''bitfield: <len=0001+X><id=5><bitfield>

    The bitfield message may only be sent immediately after the
    handshaking sequence is completed, and before any other messages are
    sent. It is optional, and need not be sent if a client has no
    pieces.

    The bitfield message is variable length, where X is the length of
    the bitfield. The payload is a bitfield representing the pieces
    that have been successfully downloaded. The high bit in the first
    byte corresponds to piece index 0. Bits that are cleared indicated a
    missing piece, and set bits indicate a valid and available piece.
    Spare bits at the end are set to zero.

    Some clients (Deluge for example) send bitfield with missing pieces
    even if it has all data. Then it sends rest of pieces as have
    messages. They are saying this helps against ISP filtering of
    BitTorrent protocol. It is called lazy bitfield.

    A bitfield of the wrong length is considered an error. Clients
    should drop the connection if they receive bitfields that are not of
    the correct size, or if the bitfield has any of the spare bits set.
    '''
    def __init__(self, bitfield):
        self.length = 1 + len(bitfield)
        self.id = 5
        self.bitfield = bitfield

    def to_bytes(self):
        r = super(BitField, self).to_bytes()
        for byte in self.bitfield:
            r += pack('!c', bytes([byte]))
        return r


class Request(Message):
    '''request: <len=0013><id=6><index><begin><length>

    The request message is fixed length, and is used to request a
    block. The payload contains the following information:

    index: integer specifying the zero-based piece index
    begin: integer specifying the zero-based byte offset within the
    piece
    length: integer specifying the requested length.
    '''
    def __init__(self, index, begin, length):
        Message.__init__(self)
        self.length = 13
        self.id = 6
        self.index = index
        self.begin = begin
        self.request_length = length

    def to_bytes(self):
        r = super(Request, self).to_bytes()
        r += pack('!l', self.index)
        r += pack('!l', self.begin)
        r += pack('!l', self.request_length)
        return r


class Piece(Message):
    '''piece: <len=0009+X><id=7><index><begin><block>

    The piece message is variable length, where X is the length of the
    block. The payload contains the following information:

    index: integer specifying the zero-based piece index
    begin: integer specifying the zero-based byte offset within the
    piece
    block (bytes): block of data, which is a subset of the piece
    specified by index.
    '''
    def __init__(self, index, begin, block):
        Message.__init__(self)
        self.length = 9 + len(block)
        self.id = 7
        self.index = index
        self.begin = begin
        self.block = block

    def to_bytes(self):
        r = super(Piece, self).to_bytes()
        r += pack('!l', self.index)
        r += pack('!l', self.begin)
        r += self.block
        return r


class Cancel(Message):
    '''cancel: <len=0013><id=8><index><begin><length>

    The cancel message is fixed length, and is used to cancel block
    requests. The payload is identical to that of the "request" message.
    It is typically used during "End Game" (see the Algorithms section
    below).
    '''
    def __init__(self, index, begin, length):
        Message.__init__(self)
        self.length = 13
        self.id = 8
        self.index = index
        self.begin = begin
        self.request_length = length

    def to_bytes(self):
        r = super(Cancel, self).to_bytes()
        r += pack('!l', self.index)
        r += pack('!l', self.begin)
        r += pack('!l', self.request_length)
        return r


class Port(Message):
    '''port: <len=0003><id=9><listen-port>

    The port message is sent by newer versions of the Mainline that
    implements a DHT tracker. The listen port is the port this peer's
    DHT node is listening on. This peer should be inserted in the local
    routing table (if DHT tracker is supported).
    '''
    def __init__(self, port):
        Message.__init__(self)
        self.length = 3
        self.id = 9
        self.listen_port = port

    def to_bytes(self):
        r = super(Port, self).to_bytes()
        r += pack('!H', self.listen_port)
        return r


if __name__ == '__main__':
    msg_queue = MessageQueue()
    m0 = Message.get_message('keep-alive')
    print(m0.to_bytes())
    m1 = Message.get_message('bitfield', bitfield=b'asdf')
    # for _ in range(5):
    #     for byte in m1.to_bytes():
    #         print(byte)
    #         msg_queue.put(byte)
    # print(msg_queue.queue)
    # print(msg_queue.get_message())
    # print(msg_queue.queue)
