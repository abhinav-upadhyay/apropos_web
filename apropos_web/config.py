#!/usr/bin/env python

MAN_DB_PATH = '/var/man.db'
APROPOS_WEB_DB_PATH = '/usr/local/apropos_web/apropos_web.db'
APROPOS_PATH='/usr/local/bin/apropos' #set a symlink to the compiled apropos
DEFAULT_CACHE_SIZE=10240
DB_PATHS={'netbsd': '/usr/local/apropos_web/netbsd/man.db',
        'posix':'/usr/local/apropos_web/posix/man.db'}
