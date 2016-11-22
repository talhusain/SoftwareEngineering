from struct import pack


class Message(object):
    def __init__(self):
        self.length = None
        self.id = None
        self.payload = None

    # Factory method for generating message objects
    @staticmethod
    def get_message(msg_type, payload=None):
        if msg_type == 'keep-alive':
            return KeepAlive()
        elif msg_type == 'choke':
            return Choke()
        elif msg_type == 'unchoke':
            return UnChoke()
        elif msg_type == 'interested':
            return Interested(payload)
        elif msg_type == 'not interested':
            pass
        elif msg_type == 'have':
            pass
        elif msg_type == 'bitfield':
            pass
        elif msg_type == 'request':
            pass
        else:
            raise ValueError('Unknown message type %s' % msg_type)

    def to_bytes(self):
        if self.length is not None:
            r = pack('!l', self.length)
        if self.id is not None:
            r += pack('!c', bytes([self.id]))
        return r


class KeepAlive(Message):
    def __init__(self):
        self.length = 0
        self.id = None
        self.payload = None


class Choke(Message):
    def __init__(self):
        self.length = 1
        self.id = 0
        self.payload = None


class UnChoke(Message):
    def __init__(self):
        self.length = 1
        self.id = 1
        self.payload = None


class Interested(Message):
    def __init__(self, payload):
        self.length = 5
        self.id = 4
        self.payload = payload

    def to_bytes(self):
        return super(Interested, self).to_bytes() + pack('!l', self.payload)


if __name__ == '__main__':
    m = Message.get_message('keep-alive')
    print(m.to_bytes())
    m = Message.get_message('interested', 0)
    print(m.to_bytes())
