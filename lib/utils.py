def sanitiseFingerprint(fpr):
    """
    Sanitise a fingerprint (of a TLS certificate, for instance) for
    comparison.  This removes colons, spaces and makes the string
    upper case.
    """

    #fpr = fpr.translate (None, ': ')
    fpr = fpr.replace (":", "")
    fpr = fpr.replace (" ", "")
    fpr = fpr.upper ()

    return fpr
