from common import *
from utils import *

from requests import *

# Stores desired fingerprints
fp_sha256 = {}

# PyOpenSSL callback
def verify_fingerprint(connection, x509, errnum, errdepth, ok):
    host = connection.get_servername()
    seen_fp = sanitiseFingerprint(x509.digest("sha256"))
    
    if app['debug']:
        print "Checking TLS cert", seen_fp, "for", host
    
    # Accept a cert if verification is forced off, or if it's a non-primary CA cert (the main cert will still be verified), or if the SHA256 matches
    return (host in fp_sha256 and sanitiseFingerprint("NONE") in fp_sha256[host]) or errdepth > 0 or (host in fp_sha256 and seen_fp in fp_sha256[host])

# Add a fingerprint to the whitelist
def add_fingerprint(host, fp):
    if host not in fp_sha256:
        fp_sha256[host] = []
    
    fp_sha256[host].append(sanitiseFingerprint(fp))

# Returns HTML analysis from SSLLabs.  Output this to a file and view with Javascript disabled.
def test_tls_config():
    return get("https://www.ssllabs.com/ssltest/viewMyClient.html").text

def init():
    # Set ciphers and enable fingerprint verification via PyOpenSSL
    packages.urllib3.contrib.pyopenssl.DEFAULT_SSL_CIPHER_LIST = "EDH+aRSA+AES256:EECDH+aRSA+AES256:!SSLv3"
    packages.urllib3.contrib.pyopenssl._verify_callback = verify_fingerprint
    packages.urllib3.contrib.pyopenssl.inject_into_urllib3()

