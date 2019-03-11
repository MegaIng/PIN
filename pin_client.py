from __future__ import annotations

import keyword
import socket
from typing import TYPE_CHECKING

from pin_common import BasePIN, decode, GET_PREFIX, SEPARATOR, encode, SET_PREFIX, DIR_PREFIX, NONE_PREFIX


class PINClient:
    def __init__(self, host: str = "localhost", port: int = 55555):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.address = host, port
        self.client.connect(self.address)

    def set(self, key, value, pin):
        self.client.send(SET_PREFIX + (pin._full_path + '.' + key).encode() + SEPARATOR + encode(value))
        data = self.client.recv(65536)
        assert data == b'OK'

    def request(self, item: str, pin: PIN):
        cmd = GET_PREFIX + (pin._full_path + '.' + item).encode()
        self.client.send(cmd)
        data = self.client.recv(65536)
        return decode(data, pin)

    def request_content(self, pin: PIN):
        self.client.send(DIR_PREFIX + pin._full_path.encode())
        data = self.client.recv(65536)
        print(data)
        if data == NONE_PREFIX:
            return ()
        return tuple(b.decode() for b in data.split(SEPARATOR))


class PIN(BasePIN):
    if TYPE_CHECKING:
        __slots__ = ('_client', '_children_cache', '__dict__')
    else:
        __slots__ = ('_client', '_children_cache')

    def __init__(self, name: str, parent: PIN = None, client: PINClient = None):
        self._name = name
        self._parent = parent
        self._client: PINClient = client or PINClient()
        self._children_cache = {}

    def __setattr__(self, key:str, value):
        if key.startswith("_"):
            return super().__setattr__(key, value)
        if not key.isidentifier() or keyword.iskeyword(key):
            raise AttributeError
        return self._client.set(key, value, self)

    def __getattr__(self, item):
        if item.startswith("_"):
            raise AttributeError("Can not use name with underscore at the beginning")
        if not item.isidentifier() or keyword.iskeyword(item):
            raise AttributeError("Can not use invalid name as attribute (not valid python identifier)")
        return self._client.request(item, self)

    def __dir__(self):
        return self._client.request_content(self)

    def _get_child(self, name: str):
        if name not in self._children_cache:
            self._children_cache[name] = PIN(name, self, self._client)
        return self._children_cache[name]
