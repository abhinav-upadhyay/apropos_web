#!/bin/sh

#Start running application using gunicorn with 2 worker threads.
#XXX Automate it better to convert it into an rc script.
/usr/pkg/bin/gunicorn --daemon --workers 2 --bind unix:apropos_web.sock -m 500 --timeout 120 wsgi:app
