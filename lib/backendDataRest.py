from common import *

import httplib
import json
import urllib
import urlparse

class backendData():
    validURL = False

    def __init__(self, conf):
        url = urlparse.urlparse(conf)
        if url.scheme == 'http':
            self.validURL = True
            self.host = url.hostname
            self.port = url.port
        elif app['debug']:
            print "Unsupported scheme for REST URL:", url.scheme

    def getAllNames(self):
        # The REST API doesn't support enumerating the names.
        return False

    def getName(self, name):
        if not self.validURL:
            return "invalid REST URL", None

        encoded = urllib.quote_plus(name)
        data = self._queryHttpGet("/rest/name/" + encoded + ".json")

        if data is None:
            return "query failed", None
        return None, json.loads(data)

    def _queryHttpGet(self, path):
        assert self.validURL
        conn = httplib.HTTPConnection(self.host, self.port)
        conn.request('GET', path)

        res = conn.getresponse()
        if res.status != 200:
            if app['debug']:
                print "REST returned error code:", res.status
                print res.read()
            return None

        return res.read()

