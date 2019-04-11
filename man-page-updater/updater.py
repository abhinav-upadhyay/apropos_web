#!/usr/bin/env python

from __future__ import print_function
import argparse
import os
import shutil
import subprocess
import tempfile
import requests
from updater_utils import *
from clint.textui import progress

MANDB_BASE_DIR = '/usr/local/apropos_web/'
HTML_BASE_DIR = '/usr/local/apropos_web/'
MANDB_STD_LOC = '/var/db/man.db'
CACHE_FILE = './.apropos_web.cache'
HOME_DIR = os.getcwd()
os.environ['HTDIR'] = 'html'
myos = None


def download_sets(set_url, filename):
    try:
        r = requests.get(set_url, stream=True)
        if r.status_code < 200 or r.status_code > 299:
            eprint('Non-200 status from sets URL: %s' % set_url)
            return None
        with open(filename, 'wb') as f:
            content_length = r.headers.get('content-length')
            total_length = int(content_length) if content_length else 8192
            for chunk in progress.bar(r.iter_content(chunk_size=1024), expected_size=(total_length/1024) + 1):
                if chunk:
                    f.write(chunk)
                    f.flush()
    except Exception as e:
        eprint('Failed to download %s from url %s because of exception %s' % (filename, set_url, str(e)))
        return None
    return r

def extract_set(set_name, tar_options):
    proc = subprocess.Popen(['tar', tar_options, set_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    if proc.returncode != 0:
        eprint('Failed to extracet %s with error: %s' % (set_name, err))
        return False
    return True

'''
Generate HTML man pages and copy them to /usr/local/apropos_web/<OS>/man/
'''
def make_html(release_man_directory, release_name):
    print('Copying Makefile to %s for generating HTML pages' % release_man_directory)
    shutil.copy(HOME_DIR + '/Makefile', release_man_directory)
    cwd = os.getcwd()
    if cwd != release_man_directory:
        os.chdir(release_man_directory)

    print('Generating HTML pages in %s' % release_man_directory)
    os.environ['OS'] = release_name
    proc = subprocess.Popen(['make', 'html'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    if proc.returncode != 0:
        eprint('Failed to generate html pages in %s' % release_man_directory)
        os.chdir(cwd)
        return False
    print(out)
    print('HTML pages generated successfully in %s' % release_man_directory)
    html_directory = HTML_BASE_DIR + release_name + '/man'
    print('Copying HTML pages to %s' % html_directory)
    if os.path.exists(html_directory):
        shutil.rmtree(html_directory, ignore_errors=False)
    shutil.copytree(release_man_directory + '/html', html_directory)
    os.chdir(cwd)
    return True

def get_base_sets(sets_url, target_directory, base_setnames, tar_options):
    cwd = os.getcwd()
    os.chdir(target_directory)
    for set_name in base_setnames:
        print('Starting download for set %s for %s' % (set_name, target_directory))
        url = sets_url + set_name
        r = download_sets(url, set_name)
        if r is None:
            eprint('Failed to download %s for %s' % (set_name, target_directory))
            return False
        print('Extracting set %s for %s' % (set_name, target_directory))
        status = extract_set(set_name, tar_options)
        if status is False:
            os.chdir(cwd)
            return False
    return True   

'''
Run makemandb(8) to index new man pages.
Use -C option to use a custom man.conf with _mandb set to 
/usr/local/apropos_web/<OS>/man.db
'''
def run_makemandb(directory, release_name):
    mandb_copy_dir = MANDB_BASE_DIR + release_name
    print('Going to run makemandb for %s' % directory)
    print('Copying man.conf to %s' % directory)
    shutil.copy(HOME_DIR + '/man.conf', directory)
    with open(directory + '/man.conf', 'a') as f:
        f.write('_mandb %s\n' %  (mandb_copy_dir + '/man.db'))

    os.environ['MANPATH'] = directory
    os.environ['MAKEMANDB_DBPATH'] = mandb_copy_dir + '/man.db'
    proc = subprocess.Popen(['makemandb', '-C', directory + '/man.conf', '-f'],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    out, err = proc.communicate()
    if proc.returncode != 0:
        eprint('Failed to index man pages from %s' % directory)
        eprint(err)
    else:
        print(out)
        print('makemandb run successful for %s' % release_name)

def actually_download_sets(history, myos, cache=False):
    release_status = {}
    cwd = os.getcwd()
    for key,value in myos.monitored_targets.iteritems():
        try:
            build_index_url = myos.BASE_URL + value
            print('Scraping %s' % build_index_url)
            sets_url, build_date = myos.get_latest_sets_url(build_index_url, history.get(key))
            if sets_url is None:
                eprint('No new build available for release %s' % key)
                continue
            tempdir = tempfile.mkdtemp()
            print('Created temp directory ' + str(tempdir))
            os.chdir(tempdir)
            print('Going to download sets from %s' % sets_url)
            os.mkdir(key)
            print('Created directory %s' % key)
            status = get_base_sets(sets_url, key, myos.get_base_setnames(key), myos.TAR_OPTIONS)
            if status:
                print('Succussfully downloaded sets for %s' % key)
                history[key] = int(build_date)
                release_status[key] = tempdir
            else:
                print('Failed to downloaded sets for %s' % key)
                print('Going to remove temporary directory %s' % tempdir)
                shutil.rmtree(tempdir)
        except Exception as e:
            eprint('Exception while getting sets for %s: %s' % (value, str(e)))
            if tempdir:
                print('Going to remove temporary directory %s' % tempdir)
                shutil.rmtree(tempdir)
        finally:
            tempdir = None

    os.chdir(cwd)
    if cache:
        with open(CACHE_FILE + '_' + myos.NAME, 'w') as cache_file:
            line = '%s=%s' % (myos.NAME, ','.join(['%s:%s' % (target, dirname) for target,dirname in release_status.items()]))
            cache_file.write(line)
            cache_file.write('\n')
    return release_status

def download_sets_if_required(history, myos, cache=False):
    cache_file_name = CACHE_FILE + '_' + myos.NAME
    if not cache or not os.path.exists(cache_file_name):
        return actually_download_sets(history, myos, cache=cache)
    else:
        release_status = {}
        with open(cache_file_name) as cache_file:
            for line in cache_file:
                line = line[:-1]
                fields = line.split('=')
                monitored_targets = fields[1].split(',')
                for target in monitored_targets:
                    target_name = target.split(':')[0]
                    dirname = target.split(':')[1]
                    release_status[target_name] = dirname
        return release_status



def get_release(cache=False):
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--os', help='OS name')
    parser.add_argument('-c', '--cache', action='store_true',
                        help='Use data from cache if available, '
                        'or download and cache for future use')
    args = parser.parse_args()
    if args.os == 'netbsd':
        import netbsd as myos
    elif args.os == 'freebsd':
        import freebsd as myos
    elif args.os == 'openbsd':
        import openbsd as myos
    else:
        eprint('Unknown OS %s' % args.os)
        return

    history = {}
    release_status = {}
    if os.path.isfile(myos.HISTORY_FILE):
        with open(myos.HISTORY_FILE, 'r') as f:
            for line in f:
                if line[:-1] == '\n':
                    line = line[:-1]
                words = line.split()
                history[words[0]] = int(words[1])

    release_status = download_sets_if_required(history, myos, cache=args.cache)
    for k,v in release_status.iteritems():
        directory_name = v + '/' + k + '/usr/share/man'
        run_makemandb(directory_name, k)
        make_html(directory_name, k)
        print('Going to remove temporary directory %s' % v)
        if not args.cache:
            shutil.rmtree(v, ignore_errors=True)

    print('Updating history file %s' % myos.HISTORY_FILE)
    with open(myos.HISTORY_FILE, 'w') as f:
        for k,v in history.iteritems():
            f.write('%s %d\n' % (k, v))


if __name__ == '__main__':
    get_release()

