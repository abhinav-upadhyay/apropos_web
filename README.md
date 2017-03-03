# A Flask based web interface for apropos(1)

In the summer of 2011, I worked on rewriting [apropos(1)] (https://github.com/abhinav-upadhyay/apropos_replacement) utility for [NetBSD] (http://netbsd.org) as part of Google Summer of Code 2011. This project attempts to develop a web interface for it.

Unlike the traditional apropos implementations, the apropos in NetBSD does full text search and has a ranking algorithm to show the most relevant results at the top. So you could run queries like [create socket] (https://man-k.org/search?q=create+socket) or [search man pages] (https://man-k.org/search?q=search+man+pages).

It also does a basic spell check for queries and offers suggestions. For example try [make directry] (https://man-k.org/search?q=make+directry)

### See it in action here: [man-k.org] (https://man-k.org)
Currently it supports searching two distributions of man pages:
* ```NetBSD``` man pages: https://man-k.org/netbsd/ or https://man-k.org
* ```Linux``` man pages: https://man-k.org/linux/
* ```posix``` man pages: https://man-k.org/posix/


###Deployment Instructions

Install all the required Python packages as mentioned in the requirements.txt file
(You may either setup a virtual environment with all those packages or just install them
 globally, whatever works)

Download mdocml-1.13.4 from http://mdocml.bsd.lv, and install it in /usr/local.

git clone the apropos_replacement repository from my github repo and checkout the
merge_netbsd_linux branch. On linux `make -f Makefile.linux`, on NetBSD run `make`
to compile it. Run make install (or just copy the apropos binary to /usr/bin).

Run makemandb -fv after building apropos in the above step. On NetBSD it should generate
the man.db database in /var/db/man.db. On Linux it should be in /var/man.db. Copy this file
to /usr/local/apropos_web/<netbsd|linux> (depending on NetBSD or Linux).

Run gunicorn to serve the flask app, with something like:
gunicorn --workers 2 --bind unix:apropos_web.sock -m 500 --timeout 120 wsgi:app

(Consider making it an rc/init script to start it automatically on server startup).

You can either make gunicorn serve the site directly, or setup a proxy with Nginx.
