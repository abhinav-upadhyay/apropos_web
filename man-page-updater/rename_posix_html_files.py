#!/usr/bin/env python

import os
import sys

html_dir = sys.argv[1]

for f in os.listdir(html_dir):
    name_parts = f.split('.')[:-1]
    section = name_parts[-1][0]
    if len(name_parts) == 2:
        name = name_parts[0]
    else:
        name = '.'.join(name_parts[:-1])
    os.rename(html_dir + f, html_dir + name + '.' + section + 'P' + '.html')
