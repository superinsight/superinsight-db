from cachetools import cached, TTLCache
class Cacher:

  timeout_five_minutes = 60 * 5
  cache = TTLCache(maxsize=100, ttl=timeout_five_minutes)

  @cached(cache)
  def set(key, value):
    Cacher.cache[key] = (value) 
    return value
  def get(key):
    if Cacher.cache.get(key) is not None:
      value = Cacher.cache[key]
      return value
    else:
      return None