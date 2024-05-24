import socket
import select
import sys
from .util import flatten_parameters_to_bytestring
from .vec3 import Vec3

""" @author: Aron Nieminen, Mojang AB"""

class RequestError(Exception):
    pass

class Connection:
    """Connection to a Minecraft Pi game"""
    RequestFailed = "Fail"

    def __init__(self, address, port, debug=False):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(10)
        self.socket.connect((address, port))
        self.socket.settimeout(60)  # doc suggests None for makefile
        self.lastSent = ""
        self.debug = debug

    def drain(self):
        """Drains the socket of incoming data"""
        while True:
            readable, _, _ = select.select([self.socket], [], [], 0.0)
            if not readable:
                break
            data = self.socket.recv(1500)
            if self.debug:
                e =  "Drained Data: <%s>\n"%data.strip()
                e += "Last Message: <%s>\n"%self.lastSent.strip()
                sys.stderr.write(e)

    def _send(self, f, *data):
        """
        Sends data. Note that a trailing newline '\n' is added here
        """
        s = b"".join([f, b"(", flatten_parameters_to_bytestring(data), b")", b"\n"])
        self.drain()
        self.lastSent = s

        self.socket.sendall(s)

    def _receive(self):
        """Receives data. Note that the trailing newline '\n' is trimmed"""
        s = self.socket.makefile("r").readline().rstrip("\n")
        if s == Connection.RequestFailed:
            raise RequestError("%s failed"%self.lastSent.strip())
        return s

    def sendReceive(self, *data):
        """Sends and receive data"""
        self._send(*data)
        return self._receive()

    def sendReceiveList(self, *data, **kwargs):
        """Send data and receive a List of items."""
        self._send(*data)
        kwargs.setdefault("sep", "|")
        return self._unmarshalList(self._receive(), **kwargs)

    def sendReceiveScalar(self, converter, *data):
        """Send data and receive a single item converted to the passed type."""
        self._send(*data)
        return self._parseScalar(converter, self._receive())

    def sendReceiveBool(self, *data):
        """Send data and receive a boolean."""
        return self.sendReceive(*data) == "true"

    def sendReceiveVec3(self, converter, *data):
        """Send data and receive a Vec3, with each coordinate converted to the passed type."""
        self._send(*data)
        return self._parseVec3(converter, self._receive())

    def sendReceiveObjectList(self, constructor, *data, **kwargs):
        """Send data and receive a List of objects created by passing the received attributes to constructor."""
        return [constructor(*o.split(",", **kwargs)) for o in (self.sendReceiveList(*data))]

    def _unmarshalList(self, dataStr, **kwargs):
        return [] if not dataStr else dataStr.split(**kwargs)

    def _parseScalar(self, converter, string):
        try:
            return converter(string)
        except ValueError:
            return None

    def _parseVec3(self, converter, string):
        try:
            return Vec3(*list(map(converter, string.split(","))))
        except ValueError:
            return None
