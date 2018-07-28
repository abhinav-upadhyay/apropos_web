from __future__ import print_function
from updater_utils import *
from bs4 import BeautifulSoup
import requests
import sys
from sys import platform
import time

BASE_URL = 'http://ftp1.us.freebsd.org/pub/FreeBSD/snapshots/amd64/'
AMD64_SETS_URL = 'amd64/'
HISTORY_FILE = '/var/freebsd_mandb_updates.log'
if platform == 'linux' or platform == 'linux2':
    TAR_OPTIONS = '-xJf'
else:
    TAR_OPTIONS='-xzf'
monitored_targets = {}
monitored_targets['FreeBSD-11.2'] = '11.2-STABLE/'
monitored_targets['FreeBSD-10.4'] = '10.4-STABLE/'
monitored_targets['FreeBSD-12.0-CURRENT'] = '12.0-CURRENT/'

base_set_names = ['base.txz']

def get_base_setnames(release_name):
    return base_set_names


def get_latest_sets_url(release_url, previous_build_date=None):
    #unlike Net or Open, here we directly use the base URL
    r = requests.get(BASE_URL)
    if r.status_code < 200 or r.status_code > 299:
        eprint('Error from URL: %s' % release_url)
        return None, None

    soup = BeautifulSoup(r.text)
    table = soup.find('table')

    for row in table.find_all('tr')[1:]:
        col = row.find_all('td')
        release_name = col[0].string.strip()
        if release_name not in monitored_targets.values():
            continue
        date_str = col[2].string.strip()
        t = time.strptime(date_str, '%Y-%b-%d %H:%M')
        nseconds = int(time.mktime(t))
        if nseconds > previous_build_date:
            return release_url, nseconds
        else:
            return None, None
    else:
        return None, None

    return None, None
