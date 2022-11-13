from cachetools import cached, TTLCache
from environment import Environment
class Cacher:
    cached_ttl = Environment.cache_mldb_resp_sec
    cache = TTLCache(maxsize=100, ttl=cached_ttl)
    @cached(cache)
    def set(key, value):
        Cacher.cache[key] = (value) 
        return value
    def get(key):
        if Cacher.cache.get(key) is not None:
            data = Cacher.cache[key]
            return data
        else:
            return None
