NYCDN_URL = 'http://nycdn.netbsd.org/pub/NetBSD-daily/'
AMD64_SETS_URL = 'amd64/binary/sets/'
HISTORY_FILE = '/var/mandb_updates.log'
monitored_targets = {}
monitored_targets['NetBSD-6'] = 'netbsd-6/'
monitored_targets['NetBSD-6-0'] = 'netbsd-6-0/'
monitored_targets['NetBSD-6-1'] = 'netbsd-6-1/'
monitored_targets['NetBSD-7'] = 'netbsd-7/'
monitored_targets['NetBSD-7-0'] = 'netbsd-7-0/'
monitored_targets['NetBSD-7-1'] = 'netbsd-7-1/'
monitored_targets['NetBSD-current'] = 'HEAD/'

base_set_names = ['base.tgz', 'comp.tgz', 'games.tgz', 'man.tgz', 'text.tgz']
xset_names = ['xbase.tgz', 'xcomp.tgz', 'xetc.tgz', 'xfont.tgz', 'xserver.tgz']
