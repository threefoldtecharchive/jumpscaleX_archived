from Jumpscale import j

# to run this example:

# next will be filled in by the template engine when this example is called
name = "{{name}}"


###### EASY EXAMPLE WITH METHOD NOT IN CLASS, USING THE CACHING FUNCTIONALITY DIRECTLY


def do(name=""):
    j.counter += 1
    print("name:%s, counter:%s" % (name, j.counter))
    if j.counter == 5:
        return j.counter
    raise j.exceptions.Base("some error")


def main():

    cache = j.core.cache.get(id="tutorial", reset=True, expiration=5)

    ##cache.get(key, method=None, expire=None, refresh=False, retry=1, die=True, **kwargs)
    # :param key: is a unique key for item to fetch out of the cache
    # :param method: the method to execute
    # :param expire: expiration in seconds (if 0 then will be same as refresh = True)
    # :param refresh: if True will execute again
    # :param retry: std 1, means will only try 1 time, otherwise will try multiple times,
    #             useful for e.g. fetching something from internet
    # :param kwargs: the arguments in kwargs form e.g. a="1"  for the method to execute
    # :param die, normally True, means will raise error if doesnt work, if False will return the error object
    # :return: the output of the method

    # WILL 5x retry the 3e time should be ok
    j.counter = 0

    counter = cache.get("test", do, retry=10, name=name)
    assert counter == 5  # counter needs to be 3 because should be ok after 3x retry

    test = None
    j.counter = 0
    cache.reset()
    try:
        cache.get("test", do, retry=2, name=name)
        test = "OK"
    except Exception as e:
        print("ok result, there should have been an error because tried 2 times but was still error")
        test = "ERROR"

    assert test == "ERROR"  # means there was error

    return name
