import pickle

# custom cache that saves over restarts (since this is running on a server not controlled by me, this will save lots of time)
# has a local cache for the current session and a cache in a file
# whenever a cache is missed, it will check the file cache, and if that is missed, it will cache it and save it to both caches
def cache(func):
    cache = {}
    def wrapper(*args, **kwargs):
        hash = str(args) + str(kwargs)
        if hash in cache:
            print("local cache hit")
            return cache[hash]
        else:
            try:
                with open("cache.pkl", "rb") as f:
                    fcache = pickle.load(f)
            except:
                fcache = {}
            if hash in fcache:
                print("file cache hit")
                cache[hash] = fcache[hash]
                return cache[hash]
            else:
                print("cache miss")
                result = func(*args, **kwargs)
                cache[hash] = result
                fcache[hash] = result
                with open("cache.pkl", "wb") as f:
                    pickle.dump(fcache, f)
                return result
    return wrapper