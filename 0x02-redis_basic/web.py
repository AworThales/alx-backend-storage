#!/usr/bin/env python3
"""Redis Module."""
import requests
import redis
from functools import wraps
from typing import Callable

cache = redis.Redis()


def store_cache(method: Callable) -> Callable:
    """Cache a value for 10 seconds."""
    @wraps(method)
    def wrapper(url):
        """The function wrapper."""
        if cache.get(url):
            return cache.get(url).decode()
        result = method(url)
        cache.setex(url, 10, result)
        return result
    return wrapper


def track_url(method: Callable) -> Callable:
    """Cache a value for 10 seconds."""
    @wraps(method)
    def wrapper(url):
        """The function wrapper."""
        cache.incr(f'count:{url}')
        return method(url)
    return wrapper


@store_cache
@track_url
def get_page(url: str) -> str:
    """Get the result of a webpage."""
    if cache.get(url):
        return cache.get(url).decode()
    result = requests.get(url)
    return result.text
