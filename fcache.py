from joblib import Memory
from functools import cache as _cache

memory = Memory(location='cache', verbose=0)

cache = memory.cache
mem_cache = _cache
