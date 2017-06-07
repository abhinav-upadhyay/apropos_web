from __future__ import print_function
from updater_utils import *
import requests
import sys

BASE_URL = 'http://nycdn.netbsd.org/pub/NetBSD-daily/'
AMD64_SETS_URL = 'amd64/binary/sets/'
HISTORY_FILE = '/var/netbsd_mandb_updates.log'
TAR_OPTIONS = 'xpzf'
monitored_targets = {}
monitored_targets['NetBSD-6'] = 'netbsd-6/'
monitored_targets['NetBSD-6-0'] = 'netbsd-6-0/'
monitored_targets['NetBSD-6-1'] = 'netbsd-6-1/'
monitored_targets['NetBSD-7'] = 'netbsd-7/'
monitored_targets['NetBSD-7-0'] = 'netbsd-7-0/'
monitored_targets['NetBSD-7-1'] = 'netbsd-7-1/'
monitored_targets['NetBSD-8'] = 'netbsd-8/'
monitored_targets['NetBSD-current'] = 'HEAD/'

base_set_names = ['base.tgz', 'comp.tgz', 'games.tgz', 'man.tgz', 'text.tgz']
xset_names = ['xbase.tgz', 'xcomp.tgz', 'xetc.tgz', 'xfont.tgz', 'xserver.tgz']

def get_base_setnames(release_name):
    return base_set_names

def get_latest_sets_url(release_url, previous_build_date=None):
    r = requests.get(release_url)
    if r.status_code < 200 or r.status_code > 299:
        eprint('Error from URL: %s' % release_url)
        return None, None

    dates = []
    lines = r.text.splitlines()
    for line in lines:
        if line.startswith('<a href'):
            date_str = line.split('</a>')[0].split('>')[1]
            dates.append(date_str)
    
    if len(dates) == 0:
        return None, None

    for date_str in reversed(dates):
        date = int(date_str[:-2])
        if previous_build_date:
            if date > previous_build_date:
                url = (release_url + date_str + AMD64_SETS_URL)
                if ping(url) is False:
                    print('No amd64 sets found at %s, trying older builds' % url)
                else:
                    return url, date
            else:
                continue
        else:
            url = (release_url + date_str + AMD64_SETS_URL)
            if ping(url) is False:
                print('No amd64 sets found at %s, trying older builds' % url)
            else:
                return  url, date

    return None, None
