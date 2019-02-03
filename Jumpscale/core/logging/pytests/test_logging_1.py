from Jumpscale import j


def test_main():
    """
    to run:


    """

    #to trigger a logger already enabled on a class
    j.clients.ssh._logger.info("test")

    j.logger.debug=True #makes sure we are having all logging on & going to redis

    j.clients.ssh._logger.info("test")

    j.shell()

    for i in range(10000):
        res = r.storedprocedure_execute("test1","a",1,i)


    assert r.hlen("logs:data:a") == 1000




    print ("OK")
