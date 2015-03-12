from common import *
from utils import *

import requests_fp
import urllib
import urlparse
import json # Hack for Debian Wheezy compatibility; remove this import when Wheezy is phased out

# This backend requires non-default modules loaded.
# If not using TLS, you can do this on Fedora with:
# yum install python-requests
# If using TLS (experimental), you can do this on Fedora with: 
# yum install python-requests pyOpenSSL python-ndg_httpsclient python-pyasn1

# TODO: Finish testing the TLS code.  Note that Bitcoin Core is probably removing TLS support soon, so TLS support is solely for things like Nginx proxies.

class backendData():
    validURL = False

    def __init__(self, conf):
        
        url = urlparse.urlparse(conf)
        if url.scheme == 'http' or url.scheme == 'https':
            self.validURL = True
            self.scheme = url.scheme
            self.tls = (url.scheme == 'https')
            self.host = url.hostname
            self.port = url.port
            
            # Sessions let us reuse TCP connections, while keeping unique identities on different TCP connections
            self.sessions = {}
            
            if self.tls:
                # Init the TLS security settings
                try:
                    requests_fp.init()
                except:
                    print "ERROR: Failed to load PyOpenSSL."
                    print "Make sure you have the right packages installed."
                    print "On Fedora, run:"
                    print "sudo yum install pyOpenSSL python-ndg_httpsclient python-pyasn1"
                    print "Other distros/OS's may be similar"
                    import os
                    os._exit(-1)
                
                if app['debug']:
                    print "WARNING: You are using the experimental REST over TLS feature.  This is probably broken and should not be used in production."

            if url.params == '':
                self.fprs = {}
            else:
                self.fprs = self._parseFprOptions(url.params)
                
                if "sha256" in self.fprs:
                    requests_fp.add_fingerprint(self.host, self.fprs["sha256"])
            
            if self.tls and "sha256" not in self.fprs:
                if app['debug']:
                    print "ERROR: REST SHA256 fingerprint missing in plugin-data.conf; REST lookups will fail."
            
            if "testTlsConfig" in self.fprs:
                testResults = requests_fp.test_tls_config()
                print "TLS test result:"
                print testResults
                import os
                os._exit(0)
        elif app['debug']:
            print "ERROR: Unsupported scheme for REST URL:", url.scheme

    def getAllNames(self):
        # The REST API doesn't support enumerating the names.
        if app['debug']:
            print 'ERROR: REST data backend does not support name enumeration; set import.mode=none or switch to a different import.from backend.'
        return (True, None) # TODO: Should this be True rather than False?  See the data plugin for usage.

    def getName(self, name, sessionId = ""):
        
        encoded = urllib.quote_plus(name)
        
        result = self._queryHttpGet(self.scheme + "://" + self.host + ":" + str(self.port) + "/rest/name/" + encoded + ".json", sessionId)
        
        try:
            resultJson = json.loads(result.text) # Hack for Debian Wheezy compatibility; use the following line instead when Wheezy is phased out
            # resultJson = result.json()
        except ValueError:
            raise Exception("Error parsing REST response.  Make sure that Namecoin Core is running with -rest option.")
        
        return (None, resultJson)
    
    def _queryHttpGet(self, url, sessionId):
        
        # set up a session if we haven't yet for this identity (Tor users will use multiple identities)
        if sessionId not in self.sessions:
            if app['debug']:
                print 'Creating new REST identity = "' + sessionId + '"'
            self.sessions[sessionId] = requests_fp.Session()
        
        return self.sessions[sessionId].get(url)
    
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
