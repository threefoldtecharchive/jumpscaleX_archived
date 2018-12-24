import urllib.request
import urllib.error
import urllib.parse
import urllib.request
import urllib.parse
import urllib.error
import base64
# import sys


from urllib.parse import urlencode, urlparse, urlunparse
import urllib.parse
import urllib.request
import urllib.error
from Jumpscale import j
JSBASE = j.application.JSBaseClass


HTTP_CREATED = 201  # from practical examples, authorization created returns 201
HTTP_OK = 200
# An authorization token was created and provided to the client in the
# Location header.
HTTP_NO_CONTENT = 204
HTTP_AUTH_REQUIRED = 401  # Authorization required.
HTTP_FORBIDDEN = 403  # Authentication failed.
HTTP_NOT_FOUND = 404

STATUS_OK = set([HTTP_CREATED, HTTP_OK, HTTP_NO_CONTENT])
STATUS_AUTH_REQ = set([HTTP_AUTH_REQUIRED, HTTP_FORBIDDEN])

AUTHORIZATION_HEADER = 'Authorization'


class HTTPError(Exception, JSBASE):

    def __init__(self, httperror, url):
        JSBASE.__init__(self)
        msg = 'Could not open http connection to url %s' % url
        data = ''
        self.status_code = None
        if isinstance(httperror, urllib.error.HTTPError):
            msg = data = httperror.read()
            self.status_code = httperror.code
        self.msg = msg
        self.data = data
        self.httperror = httperror

    def __str__(self):
        return "%s:\n %s" % (self.status_code, self.msg)


class Connection(j.builder._BaseClass):

    def __init__(self):
        JSBASE.__init__(self)

    def simpleAuth(self, url, username, password):
        """
        authorize with the given username and password on url
        """
        req = urllib.request.Request(url)
        auth = '%s:%s' % (username, password)
        base64string = base64.encodebytes(auth.encode())[:-1]
        req.add_header("Authorization", "Basic %s" % base64string)

        try:
            handle = urllib.request.urlopen(req)
            return handle
        except IOError as e:
            raise RuntimeError("could not do simple auth.\n%s"%e)

    def get(self, url, data=None, headers=None, **params):
        """
        @params is parameters as used in get e.g. name="kds",color="red"
        @headers e.g. headers={'content-type':'text/plain'}  (this is the default)
        """
        response = self._http_request(
            url, headers=headers, method='GET', **params)  # TODO: P1 fix & check
        return response

    def get_head(self,url):
        """
        get head only, this to make sure you don't have to download everything
        """
        response = self._http_request(url, method='HEAD')  
        return response        

    def ping(self,url):
        """
        """
        try:
            r=self.get_head(url)
        except Exception as e:
            # check=[401,402,403,404,405]
            # for tocheck in check:
            #     str_e=str(e)                
            #     if str(tocheck) in str(e):
            #         return False
            if "401" in str(e): #means unauthorized so could be there, cannot check
                return True
            return False
        return r.status == 200
        

    def post(self, url, data=None, headers=None, **params):
        """
        @data is the raw aata which will be posted, if not params will be converted to json
        @params @question what are the params for?
        @headers e.g. headers={'content-type':'text/plain'}  (this is the default)
        """
        if headers is None:
            headers = {'content-type': 'text/plain'}

        response = self._http_request(
            url, data=data, headers=headers, method='POST', **params)
        return response

    def put(self, url, data=None, headers=None, **params):
        """
        @data is the raw data which will be sent
        @headers e.g. headers={'content-type':'text/plain'}  (this is the default)
        """
        response = self._http_request(
            url, data=data, headers=headers, method='PUT', **params)
        return response

    def delete(self, url, data=None, headers=None, **params):
        """
        @data is the raw data which will be sent
        @headers e.g. headers={'content-type':'text/plain'}  (this is the default)
        """
        response = self._http_request(
            url, data=data, headers=headers, method='DELETE', **params)
        return response

    def download(self, fileUrl, downloadPath, customHeaders=None, report=False):
        '''
        Download a file from server to a local path

        @param fileUrl: url of an existing file that has its data available on server (sent earlier)
        @param downloadPath: local directory to download into
        @param customHeaders: allows this method to be used to retrieve edited copies of an image
        @return: True
        '''

        # # _urlopener    = urllib.request.FancyURLopener()
        # _urlopener=urllib2.urlopen
        # if customHeaders:
        #     for k, v in list(customHeaders.items()):
        #         _urlopener.addheader(k, v)
        # _urlopener.retrieve(fileUrl, downloadPath, None, None)
        # return True

        url = fileUrl
        u = urllib.request.urlopen(url)

        scheme, netloc, path, query, fragment = urllib.parse.urlsplit(url)

        with open(downloadPath, 'wb') as f:
            meta = u.info()
            meta_func = meta.getheaders if hasattr(
                meta, 'getheaders') else meta.get_all
            meta_length = meta_func("Content-Length")
            file_size = None
            if meta_length:
                file_size = int(meta_length[0])
            if report:
                self._logger.debug(("Downloading: {0} Bytes: {1}".format(url, file_size)))

            file_size_dl = 0
            block_sz = 8192
            while True:
                buffer = u.read(block_sz)
                if not buffer:
                    break

                file_size_dl += len(buffer)
                f.write(buffer)
                if report:
                    status = "{0:16}".format(file_size_dl)
                    if file_size:
                        status += "   [{0:6.2f}%]".format(
                            file_size_dl * 100 / file_size)
                    status += chr(13)
                    self._logger.debug(status)

    def _updateUrlParams(self, url, **kwargs):
        """
        update the params of the url
        """
        _scheme, _netloc, _url, _params, _query, _fragment = urlparse(url)
        params = urllib.parse.parse_qs(_query)
        # parse_qs puts the values in a list which corrupts the url later on
        for k, v in list(params.items()):
            params[k] = v.pop() if isinstance(v, list) else v

        for k, v in list(kwargs.items()):
            if v is not None:
                params[k] = v
        _query = urllib.parse.urlencode(params)
        return urlunparse((_scheme, _netloc, _url, _params, _query, _fragment))

    def _http_request(self, url, data=None, headers=None, method=None, **kwargs):
        """
        utility function for sending an http request

        @url url of the request
        @data data to be sent with the request
        @headers headers to be sent with the request
        @method method by which we will send the request, get, post, ..

        :raises HTTPError when not able to make the request
        :raises Exception when receiving response code represent error

        :returns the response of calling the http request
        """
        url = self._updateUrlParams(url, **kwargs)
        data = data or kwargs.get('data', None)
        if data and isinstance(data, (dict, list)):
            data = urllib.parse.urlencode(data)
            data = data.encode('utf-8')
        request = urllib.request.Request(url, data=data)
        if headers:
            for key, value in list(headers.items()):
                request.add_header(key, value)
        if not method:
            method = 'POST' if data else 'GET'
        request.get_method = lambda: method
        try:
            resp = urllib.request.urlopen(request)
        except Exception as e:
            raise HTTPError(e, url)

        #if resp.code in STATUS_AUTH_REQ: raise AuthorizationError('Not logged in or token expired')
        if resp.code not in (STATUS_OK):
            raise Exception(
                'unexpected HTTP response status %s: %s' % resp.code, resp)
        return resp


class HttpClient(j.builder._BaseClass):

    def __init__(self):
        self.__jslocation__ = "j.clients.http"
        JSBASE.__init__(self)

    def getConnection(self):
        """
        :returns connection instance
        """
        connection = Connection()
        return connection

    def ping(self,url):
        # Use unverified ssl context for pinging websites
        import ssl
        ssl._create_default_https_context = ssl._create_unverified_context
        c = self.getConnection()
        res = c.ping(url)
        ssl._create_default_https_context = ssl.create_default_context
        return res

    def download(self,url,dest):
        c=self.getConnection()
        return c.download(url,dest)

    def get(self,url,dest):
        c=self.getConnection()
        return c.get(url)

    def test(self):
        """
        js_shell 'j.clients.http.test()'
        """
        c=self.getConnection()
        assert c.ping("https://github.com/Jumpscale")==True

        assert c.ping("https://something/j")==False

        assert c.ping("https://docs.grid.tf/dividi/values/src/branch/master/veda_values.md") == True #authentication error

        # assert c.ping("https://www.linkedin.com/in/babenkonickolay/") == False
        
