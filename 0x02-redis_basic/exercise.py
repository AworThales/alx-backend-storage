#!/usr/bin/env python3
""" The Redis module. """

from functools import wraps
import redis
import sys
from typing import Union, Optional, Callable
from uuid import uuid4



def call_history(method: Callable) -> Callable:
    """ Call history. """
    key = method.__qualname__
    t = "".join([key, ":inputs"])
    a = "".join([key, ":outputs"])
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """ Wrapp """
        self._redis.rpush(t, str(args))
        response = method(self, *args, **kwargs)
        self._redis.rpush(a, str(response))
        return response
    return wrapper


def replay(method: Callable):
    """ Replay. """
    key = method.__qualname__
    t = "".join([key, ":inputs"])
    a = "".join([key, ":outputs"])
    count = method.__self__.get(key)
    t_list = method.__self__._redis.lrange(t, 0, -1)
    a_list = method.__self__._redis.lrange(a, 0, -1)
    queue = list(zip(t_list, a_list))
    print(f"{key} was called {decode_utf8(count)} times:")
    for k, v, in queue:
        k = decode_utf8(k)
        v = decode_utf8(v)
        print(f"{key}(*{k}) -> {v}")


def count_calls(method: Callable) -> Callable:
    """ Count calls """
    key = method.__qualname__
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """ Wrapp """
        self._redis.incr(key)
        return method(self, *args, **kwargs)
    return wrapper


def decode_utf8(b: bytes) -> str:
    """ Decodes """
    return b.decode('utf-8') if type(b) == bytes else b


class Cache:
    """ Cache class. """

    def __init__(self):
        """ Init """
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    @call_history
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """ Random to store """
        key = str(uuid4())
        self._redis.set(key, data)
        return key

    def get(self, key: str, fn: Optional[Callable] = None) -> Union[str,
                                                                    bytes,
                                                                    int,
                                                                    float]:
        """ Gets  """
        response = self._redis.get(key)
        return fn(response) if fn else response

    def get_str(self, data: bytes) -> str:
        """ Bytes to string """
        return data.decode('utf-8')

    def get_int(self, data: bytes) -> int:
        """ Bytes to integer """
        return int.from_bytes(data, sys.byteorder)
