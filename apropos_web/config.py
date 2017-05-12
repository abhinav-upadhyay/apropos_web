#!/usr/bin/env python
from collections import OrderedDict

DB_PATHS = OrderedDict()

MAN_DB_PATH = '/var/db/man.db'
APROPOS_WEB_DB_PATH = '/usr/local/apropos_web/apropos_web.db'
APROPOS_PATH='/usr/bin/apropos' #set a symlink to the compiled apropos
DEFAULT_CACHE_SIZE=10240
DISTANCE_PATH='/usr/local/bin/similar_words'
BOW_FILE='/usr/local/apropos_web/bow.bin'
SGRAM_FILE='/usr/local/apropos_web/sgram.bin'
DB_PATHS['NetBSD-current'] = '/usr/local/apropos_web/NetBSD-current/man.db'
DB_PATHS['NetBSD-7-1'] = '/usr/local/apropos_web/NetBSD-7-1/man.db'
DB_PATHS['NetBSD-7'] = '/usr/local/apropos_web/NetBSD-7/man.db'
DB_PATHS['NetBSD-7-0']  =  '/usr/local/apropos_web/NetBSD-7-0/man.db'
DB_PATHS['NetBSD-6-1'] = '/usr/local/apropos_web/NetBSD-6-1/man.db'
DB_PATHS['NetBSD-6-0'] = '/usr/local/apropos_web/NetBSD-6-0/man.db'
DB_PATHS['NetBSD-6'] = '/usr/local/apropos_web/NetBSD-6/man.db'
DB_PATHS['posix-2013'] = '/usr/local/apropos_web/posix-2013/man.db'
DB_PATHS['posix-2003'] = '/usr/local/apropos_web/posix-2003/man.db'
DB_PATHS['OpenBSD-6.1'] = '/usr/local/apropos_web/OpenBSD-6.1/man.db'
DB_PATHS['OpenBSD-6.0'] = '/usr/local/apropos_web/OpenBSD-6.0/man.db'
DB_PATHS['FreeBSD-12.0-CURRENT'] = '/usr/local/apropos_web/FreeBSD-12.0-CURRENT/man.db'
DB_PATHS['FreeBSD-11.0'] = '/usr/local/apropos_web/FreeBSD-11.0/man.db'
DB_PATHS['FreeBSD-10.3'] = '/usr/local/apropos_web/FreeBSD-10.3/man.db'
DB_PATHS['Linux-4.11'] = '/usr/local/apropos_web/Linux-4.11/man.db'
