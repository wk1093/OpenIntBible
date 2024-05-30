from joblib import Memory
from functools import cache as mem_cache

memory = Memory(location='cache', verbose=0)

cache = memory.cache