from __future__ import annotations

import struct
from functools import reduce
from typing import Any, Optional


class BasePIN:
    __slots__ = ('_name', '_parent')
    _name: str
    _parent: Optional[BasePIN]

    def __repr__(self):
        return f"<{type(self).__name__}: {self._full_path}>"

    @property
    def _full_path(self):
        return self._name if self._parent is None else self._parent._full_path + '.' + self._name

    def _get_child(self, name: str):
        raise NotImplementedError

    def get(self, path: str):
        path = path.split('.')
        obj = self
        for e in path:
            obj = getattr(obj, e)
        return obj

    def set(self, path: str, value):
        path = path.split('.')
        obj = self
        for e in path[:-1]:
            obj = getattr(obj, e)
        setattr(obj, path[-1], value)


# region commands

GET_CODE = 0x10
DIR_CODE = 0x11
SET_CODE = 0x20

SEPARATOR_CODE = 0x00

GET_PREFIX = bytes([GET_CODE])
DIR_PREFIX = bytes([DIR_CODE])
SET_PREFIX = bytes([SET_CODE])
SEPARATOR = bytes([SEPARATOR_CODE])

# endregion

# region object codes

PIN_CODE = 0x80

STRING_CODE = 0x90
BYTES_CODE = 0x91
INT_CODE = 0x92
FLOAT_CODE = 0x93
NONE_CODE = 0x94

PIN_PREFIX = bytes([PIN_CODE])
STRING_PREFIX = bytes([STRING_CODE])
BYTES_PREFIX = bytes([BYTES_CODE])
INT_PREFIX = bytes([INT_CODE])
FLOAT_PREFIX = bytes([FLOAT_CODE])
NONE_PREFIX = bytes([NONE_CODE])


# endregion

def encode(obj: Any) -> bytes:
    if isinstance(obj, BasePIN):
        return PIN_PREFIX + obj._name.encode()
    elif isinstance(obj, str):
        return STRING_PREFIX + obj.encode()
    elif isinstance(obj, bytes):
        return BYTES_PREFIX + obj
    elif isinstance(obj, int):
        return INT_PREFIX + obj.to_bytes((obj.bit_length() + 7) // 8, 'big', signed=True)
    elif isinstance(obj, float):
        return FLOAT_PREFIX + struct.pack(">d", obj)
    elif obj is None:
        return NONE_PREFIX
    else:
        raise ValueError(repr(obj))


def decode(data: bytes, pin: BasePIN) -> Any:
    if data[0] == PIN_CODE:
        path = data[1:].decode().split('.')
        if path[0] == pin._name and pin._parent is None:
            path = path[1:]
        return reduce(lambda x, n: x._get_child(n), path, pin)
    elif data[0] == STRING_CODE:
        return data[1:].decode()
    elif data[0] == BYTES_CODE:
        return data[1:]
    elif data[0] == INT_CODE:
        return int.from_bytes(data[1:], 'big')
    elif data[0] == FLOAT_CODE:
        return struct.unpack('>d', data[1:])[0]
    else:
        raise ValueError(data)
