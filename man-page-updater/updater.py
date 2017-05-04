#!/usr/bin/env python

from __future__ import print_function
from clint.textui import progress
import os
import requests
import shutil
import subprocess
import sys
import tempfile

NYCDN_URL = 'https://nycdn.netbsd.org/pub/NetBSD-daily/'
AMD64_SETS_URL = 'amd64/binary/sets/'
HISTORY_FILE = '.mandb_updates.log'
MANDB_BASE_DIR = '/usr/local/apropos_web/'
MANDB_STD_LOC = '/var/db/man.db'
HOME_DIR = os.getcwd()

monitored_targets = {}
#monitored_targets['NETBSD_6'] = 'netbsd-6/'
#monitored_targets['NETBSD_6_0'] = 'netbsd-6-0/'
#monitored_targets['NETBSD_6_1'] = 'netbsd-6-1/'
#monitored_targets['NETBSD_7'] = 'netbsd-7/'
#monitored_targets['NETBSD_7_0'] = 'netbsd-7-0/'
#monitored_targets['NETBSD_7_1'] = 'netbsd-7-1/'
monitored_targets['HEAD'] = 'HEAD/'

#base_set_names = ['base.tgz']#, 'comp.tgz', 'etc.tgz', 'games.tgz', 'man.tgz',
#'misc.tgz', 'modules.tgz', 'tests.tgz', 'text.tgz' 
#]
base_set_names = ['man.tgz']

xset_names = ['xbase.tgz', 'xcomp.tgz', 'xetc.tgz', 'xfont.tgz', 'xserver.tgz']

os.environ['HTDIR'] = 'html'

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

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

    if previous_build_date is None:
        return (release_url + dates[-1] + AMD64_SETS_URL, dates[-1][:-2])

    for date_str in reversed(dates):
        date = int(date_str[:-2])
        if date > previous_build_date:
            return (release_url + date_str + AMD64_SETS_URL, date)
    return None, None

def download_sets(set_url, filename):
    try:
        r = requests.get(set_url, stream=True)
        if r.status_code < 200 or r.status_code > 299:
            eprint('Non-200 status from sets URL: %s' % set_url)
            return None
        with open(filename, 'wb') as f:
            total_length = int(r.headers.get('content-length'))
            for chunk in progress.bar(r.iter_content(chunk_size=1024), expected_size=(total_length/1024) + 1):
                if chunk:
                    f.write(chunk)
                    f.flush()
    except Exception as e:
        eprint('Failed to download %s from url %s because of exception %s' % (filename, set_url, str(e)))
        return None
    return r

def extract_set(set_name):
    proc = subprocess.Popen(['tar', '-xpzf', set_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    if proc.returncode != 0:
        eprint('Failed to extracet %s with error: ' % (set_name, err))
        return False
    return True

def make_html(release_directory):
    shutil.copy(HOME_DIR + '/Makefile', release_directory)
    cwd = os.getcwd()
    if cwd != release_directory:
        os.chdir(release_directory)

    proc = subprocess.Popen(['make', 'html'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    if proc.returncode != 0:
        eprint('Failed to generate html pages in %s' % release_directory)
        os.chdir(cwd)
        return False
    print(out)
    os.chdir(cwd)
    return True

def get_base_sets(sets_url, target_directory):
    cwd = os.getcwd()
    os.chdir(target_directory)
    for set_name in base_set_names:
        print('Starting download for set %s for %s' % (set_name, target_directory))
        url = sets_url + set_name
        r = download_sets(url, set_name)
        if r is None:
            eprint('Failed to download %s for %s' % (set_name, target_directory))
            return False
        print('Extracting set %s for %s' % (set_name, target_directory))
        status = extract_set(set_name)
        if status is False:
            os.chdir(cwd)
            return False
    return True   

def run_makemandb(directory, release_name):
    os.environ['MANPATH'] = directory
    proc = subprocess.Popen(['makemandb', '-v'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    if proc.returncode != 0:
        eprint('Failed to index man pages from %s' % directory)
        eprint(err)
    else:
        print(out)
        shutil.copy(MANDB_STD_LOC, MANDB_BASE_DIR + release_name + '/man.db')


def get_release():
    history = {}
    release_status = {}
    tempdir = None
    if os.path.isfile(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            for line in f:
                if line[:-1] == '\n':
                    line = line[:-1]
                words = line.split()
                history[words[0]] = int(words[1])

    cwd = os.getcwd()
    for key,value in monitored_targets.iteritems():
        build_index_url = NYCDN_URL + value
        print('Scraping %s' % build_index_url)
        sets_url, build_date = get_latest_sets_url(build_index_url, history.get(key))
        if sets_url is None:
            eprint('No new build available for release %s' % key)
            continue
        if tempdir is None:
            tempdir = tempfile.mkdtemp()
            print('Created temp directory ' + str(tempdir))
            os.chdir(tempdir)
        print('Going to download sets from %s' % sets_url)
        os.mkdir(key)
        print('Created directory %s' % key)
        status = get_base_sets(sets_url, key)
        if status:
            print('Succussfully downloaded sets for %s' % key)
            history[key] = int(build_date)
            release_status[key] = True
        else:
            print('Failed to downloaded sets for %s' % key)
            release_status[key] = False

    if tempdir is not None:
        os.chdir(cwd)

    for k,v in release_status.iteritems():
        if v is True:
            directory_name = tempdir + '/' + k + '/usr/share/man'
            make_html(directory_name)
            run_makemandb(tempdir + '/' + k, k)
            

    print('Updating history file')
    with open(HISTORY_FILE, 'w') as f:
        for k,v in history.iteritems():
            f.write('%s %d' % (k, v))


if __name__ == '__main__':
    get_release()

