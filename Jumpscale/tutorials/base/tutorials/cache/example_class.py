from Jumpscale import j
import time
JSBASE = j.application.JSBaseClass

class TutorialCacheClass(JSBASE):
    """
    """

    def __init__(self):
        JSBASE.__init__(self)
        self.value = 1

        # self._logger_enable()


    def amounts_servers_active(self,reload=False):

        def do(me=None):
            print("self.value:%s"%me.value)
            #SLOW FUNCTION
            #Get something from webservice but it could fail
            #ok to cache for 60 sec
            x=j.data.idgenerator.generateRandomInt(1,5)
            print(x)
            if x==2:
                #simulator that once and a while I get the return from internet, here 1 time on 10 it works
                return me.value
            else:
                msg = "could not fetch info, there was simulated network error"
                print(msg)
                time.sleep(0.05)
                raise RuntimeError(msg)
        return self._cache.get("amounts_servers_active",do,expire=60,retry=100,refresh=reload,me=self)

def main():

    c=TutorialCacheClass()
    c.cache.reset()
    c.value = 1
    print("FIRST QUERY, value needs to be 1")
    assert c.amounts_servers_active()==1
    c.value = 2
    print("2nd QUERY, value needs to be 1, because cache will return")
    #now will go immediate because cached
    assert c.amounts_servers_active()==1
    #now will empty cache
    c.value = 3
    print("2nd QUERY, value needs to be 3, because cache is emptied")
    assert c.amounts_servers_active(reload=True)==3
    print("test done ok")






