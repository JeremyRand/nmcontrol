from common import *
from utils import *

import hashlib
import httplib
import json
import socket
import ssl
import urllib
import urlparse

class MyHTTPSConnection(httplib.HTTPConnection):
    """
    Make a HTTPS connection, but support checking the
    server's certificate fingerprint.
    """

    def __init__(self, host, port):
        httplib.HTTPConnection.__init__(self, host, port)

    def connect(self):
        sock = socket.create_connection((self.host, self.port))
        self.sock = ssl.wrap_socket(sock)

    def verifyCert(self, fprs):
        """
        Check whether the server's certificate fingerprint
        matches the given one.  'fprs' should be a dict with
        keys corresponding to digest methods and values being
        the digest value.
        """

        hasher = None
        fpr = None
        
        if 'sha256' in fprs:
            hasher = hashlib.sha256()
            fpr = fprs['sha256']
        elif 'sha1' in fprs:
            hasher = hashlib.sha1()
            fpr = fprs['sha1']

        # Be strict here.  If this routine is called, it means that at least
        # some parameters were given in the REST URI.  If we can't verify the
        # fingerprint because the parameters were invalid, fail to make sure
        # that the user does not expect security but doesn't get it due
        # to an operational mistake.
        if hasher is None:
            if app['debug']:
                print "no recognised fingerprint given, failing check"
            return False
        assert fpr is not None

        cert = self.sock.getpeercert(True)
        hasher.update(cert)
        digest = hasher.hexdigest()

        if sanitiseFingerprint(digest) != sanitiseFingerprint(fpr):
            if app['debug']:
                print "Fingerprint mismatch:"
                print "  expected:", fpr
                print "  got:", digest
            return False

        return True

class backendData():
    validURL = False

    def __init__(self, conf):
        url = urlparse.urlparse(conf)
        if url.scheme == 'http' or url.scheme == 'https':
            self.validURL = True
            self.tls = (url.scheme == 'https')
            self.host = url.hostname
            self.port = url.port

            if url.params == '':
                self.fprs = None
            else:
                self.fprs = self._parseFprOptions(url.params)
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
        if self.tls:
            conn = MyHTTPSConnection(self.host, self.port)
        else:
            conn = httplib.HTTPConnection(self.host, self.port)
        conn.request('GET', path)

        if self.tls and (self.fprs is not None):
            if not conn.verifyCert(self.fprs):
                return "TLS fingerprint wrong", None

        res = conn.getresponse()
        if res.status != 200:
            if app['debug']:
                print "REST returned error code:", res.status
                print res.read()
            return None

        return res.read()

    def _parseFprOptions(self, s):
        """
        Parse the REST URI params string that includes (optionally)
        the TLS certificate fingerprints.
        """

        pieces = s.split(',')

        res = {}
        for p in pieces:
            parts = p.split('=', 1)
            assert len (parts) <= 2
            if len (parts) == 2:
                res[parts[0]] = parts[1]

        return res
