from __future__ import print_function
import requests
import sys

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def ping(url):
    try:
        print('Pinging %s' % url)
        r = requests.get(url)
        if r.status_code < 200 or r.status_code > 299:
            return False
        return True
    except Exception as e:
        eprint('Exception while pinging %s: %s' % (url, str(e)))
        return False
