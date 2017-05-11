#!/usr/bin/env python

MAN_DB_PATH = '/var/db/man.db'
APROPOS_WEB_DB_PATH = '/usr/local/apropos_web/apropos_web.db'
APROPOS_PATH='/usr/bin/apropos' #set a symlink to the compiled apropos
DEFAULT_CACHE_SIZE=10240
DISTANCE_PATH='/usr/local/bin/similar_words'
BOW_FILE='/usr/local/apropos_web/bow.bin'
SGRAM_FILE='/usr/local/apropos_web/sgram.bin'
DB_PATHS={
        'NetBSD-6': '/usr/local/apropos_web/NetBSD-6/man.db',
        'NetBSD-6-0': '/usr/local/apropos_web/NetBSD-6-0/man.db',
        'NetBSD-6-1': '/usr/local/apropos_web/NetBSD-6-1/man.db',
        'NetBSD-7': '/usr/local/apropos_web/NetBSD-7/man.db',
        'NetBSD-7-0': '/usr/local/apropos_web/NetBSD-7-0/man.db',
        'NetBSD-7-1': '/usr/local/apropos_web/NetBSD-7-1/man.db',
        'NetBSD-current': '/usr/local/apropos_web/NetBSD-current/man.db',
        'posix':'/usr/local/apropos_web/posix/man.db',
        'OpenBSD-6.1':'/usr/local/apropos_web/OpenBSD-6.1/man.db',
        'OpenBSD-6.0':'/usr/local/apropos_web/OpenBSD-6.0/man.db',
        'Linux':'/usr/local/apropos_web/linux/man.db'}
