#!/usr/bin/env python

MAN_DB_PATH = '/var/db/man.db'
APROPOS_WEB_DB_PATH = '/usr/local/apropos_web/apropos_web.db'
APROPOS_PATH='/usr/bin/apropos' #set a symlink to the compiled apropos
DEFAULT_CACHE_SIZE=10240
DISTANCE_PATH='/usr/local/bin/similar_words'
BOW_FILE='/usr/local/apropos_web/bow.bin'
SGRAM_FILE='/usr/local/apropos_web/sgram.bin'
DB_PATHS={'netbsd': '/usr/local/apropos_web/netbsd/man.db',
        'posix':'/usr/local/apropos_web/posix/man.db',
        'openbsd':'/usr/local/apropos_web/openbsd/man.db',
        'linux':'/usr/local/apropos_web/linux/man.db'}
