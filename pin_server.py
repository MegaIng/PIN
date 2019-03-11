from __future__ import annotations

import socket
from dataclasses import dataclass
from functools import reduce
from typing import Dict, Any, List

from pin_common import encode, BasePIN, GET_CODE, SET_CODE, SEPARATOR, decode, DIR_CODE, NONE_PREFIX


@dataclass(repr=False)
class PIN(BasePIN):
    def _get_child(self, name: str):
        return self[name]

    _name: str
    _children: Dict[str, Any]
    _parent: Any = None

    def __getitem__(self, item):
        if item not in self._children:
            self._children[item] = PIN(item, {}, self)
        return self._children[item]

    def __setitem__(self, key, value):
        self._children[key] = value


class PINServer:
    def __init__(self, host: str = "localhost", port: int = 55555):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.address = host, port
        self.server.bind(self.address)
        self.data = PIN('pin', {})
        self.clients: List[socket.socket] = []

    def store(self):
        raise NotImplementedError

    def close(self):
        print("Clean up")
        self.server.close()
        self.store()

    def run(self):
        self.server.listen(5)
        self.server.setblocking(False)
        try:
            while True:
                self.accept_clients()
                self.handle_clients()
        finally:
            self.close()

    def accept_clients(self):
        try:
            while True:
                self.clients.append(self.server.accept()[0])
        except BlockingIOError:
            return

    def handle_clients(self):
        for client in self.clients:
            try:
                data = client.recv(2048)
                if data == b'':
                    self.clients.remove(client)
                    continue
                print(data)
                if data[0] == GET_CODE:
                    self.handle_get(client, data[1:])
                elif data[0] == DIR_CODE:
                    self.handle_dir(client, data[1:])
                elif data[0] == SET_CODE:
                    self.handle_set(client, data[1:])
                else:
                    raise ValueError
            except BlockingIOError:
                continue
            except ConnectionResetError:
                self.clients.remove(client)

    def handle_get(self, client, data):
        path = data.decode().split('.')
        if path[0] == self.data._name:
            path = path[1:]
        obj = reduce(lambda x, n: x[n], path, self.data)
        print('get', path, obj)
        client.send(encode(obj))

    def handle_dir(self, client, data):
        path = data.decode().split('.')
        if path[0] == self.data._name:
            path = path[1:]
        obj = reduce(lambda x, n: x[n], path, self.data)
        print('dir', path, obj)
        assert isinstance(obj, PIN)
        client.send(SEPARATOR.join(name.encode() for name in obj._children) or NONE_PREFIX)

    def handle_set(self, client, data):
        d1, _, d2 = data.partition(SEPARATOR)
        path = d1.decode().split('.')
        if path[0] == self.data._name:
            path = path[1:]
        pin = reduce(lambda x, n: x[n], path[:-1], self.data)
        obj = decode(d2, pin)
        print('set', path, obj)
        pin[path[-1]] = obj
        client.send(b'OK')


if __name__ == '__main__':
    PINServer().run()
