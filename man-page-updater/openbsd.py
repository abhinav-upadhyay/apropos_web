from __future__ import print_function
from updater_utils import *
import requests
import sys
import time

BASE_URL = 'http://mirrors.evowise.com/pub/OpenBSD/'
AMD64_SETS_URL = 'amd64/'
HISTORY_FILE = '/var/openbsd_mandb_updates.log'
monitored_targets = {}
monitored_targets['OpenBSD-6.1'] = '6.1/'
monitored_targets['OpenBSD-6-0'] = '6.0/'
monitored_targets['OpenBSD-5-9'] = '5.9/'

base_set_names = ['base%d.tgz', 'comp%d.tgz', 'game%d.tgz', 'man%d.tgz']

def get_base_setnames(release_name):
    release_number = ''
    for c in release_name:
        if c == '.':
            continue
        release_number += c
    names = [(setname % release_number) for setname in base_set_names]
    return names


def get_latest_sets_url(release_url, previous_build_date=None):
    r = requests.get(release_url)
    if r.status_code < 200 or r.status_code > 299:
        eprint('Error from URL: %s' % release_url)
        return None, None

    lines = r.text.splitlines()
    for line in lines:
        if not line.startswith('<a href'):
            continue
        if line.find('amd64') != -1:
            date_parts = line.split('</a>')[1].strip().split()[0:2]
            date_str = date_parts[0] + ' ' + date_parts[1]
            t = time.strptime(date_str, '%d-%M-%Y %H:%M')
            nseconds = int(time.mktime(t))
            if nseconds > previous_build_date:
                return release_url + '/amd64', nseconds
            else:
                return None, None

    else:
        return None, None
