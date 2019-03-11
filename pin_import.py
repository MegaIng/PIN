from importlib.machinery import ModuleSpec
from importlib.abc import Loader, Finder, MetaPathFinder

import sys
from typing import List

from pin_client import PIN, PINClient

DEFAULT_HOST = "localhost"
DEFAULT_PORT = 55555


def get_pin_client(host=None, port=None) -> PINClient:
    if getattr(get_pin_client, "pin_client", None) is None:
        get_pin_client.pin_client = PINClient(host or DEFAULT_HOST, port or DEFAULT_PORT)
    else:
        client = get_pin_client.pin_client
        if host is not None and client.address[0] != host:
            raise ValueError("Requested host does not match already connected host.")
        if port is not None and client.address[1] != port:
            raise ValueError("Requested port does not match already connected port.")
    return get_pin_client.pin_client


class _PINModule:
    __pin__: PIN

    def __init__(self, pin: PIN):
        self.__pin__ = pin

    def __getattr__(self, item):
        return getattr(self.__pin__, item)

    def __setattr__(self, key, value):
        if key.startswith('__') and key.endswith('__'):
            return super(_PINModule, self).__setattr__(key, value)
        else:
            if hasattr(value, '__pin__'):
                value = value.__pin__
            return setattr(self.__pin__, key, value)


class PINImporter(MetaPathFinder, Loader):
    def find_spec(self, full_name: str, path, target=None):
        parts = full_name.split('.')
        if parts[0] != 'pin':
            return None
        root = PIN('pin', None, get_pin_client())
        if full_name != 'pin':
            v = root.get(full_name[4:])
            if not isinstance(v, PIN):
                raise ImportError("Can not import none namespace PIN-Value")
        else:
            v = root
        spec = ModuleSpec(full_name, self, is_package=True)
        return spec

    def create_module(self, spec: ModuleSpec):
        pin = PIN('pin', None, get_pin_client())
        if spec.name != 'pin':
            pin = pin.get(spec.name[4:])
        return _PINModule(pin)

    def exec_module(self, module):
        module.__all__ = dir(module.__pin__)


sys.meta_path.insert(0, PINImporter())
