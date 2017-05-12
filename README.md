# A Flask based web interface for apropos(1)

In the summer of 2011, I worked on rewriting [apropos(1)] (https://github.com/abhinav-upadhyay/apropos_replacement) utility for [NetBSD] (http://netbsd.org) as part of Google Summer of Code 2011. This project attempts to develop a web interface for it.

Unlike the traditional apropos implementations, the apropos in NetBSD does full text search and has a ranking algorithm to show the most relevant results at the top. So you could run queries like [create socket] (https://man-k.org/search?q=create+socket) or [search man pages] (https://man-k.org/search?q=search+man+pages).

It also does a basic spell check for queries and offers suggestions. For example try [make directry] (https://man-k.org/search?q=make+directry)

### See it in action here: [man-k.org] (http://man-k.org)
Currently it supports following searching man pages for following operating systems:
* ```NetBSD``` 
* ```FreeBSD```
* ```OpenBSD```
* ```Linux``` 
* ```POSIX-2013``` 
* ```POSIX-2003```


### Deployment Instructions

* Install all the required Python packages as mentioned in the requirements.txt file
(You may either setup a virtual environment with all those packages or just install them
 globally, whatever works)

* Clone mdocml-1.14.1 from https://github.com/abhinav-upadhyay/mdocml, and install it in /usr/local.
(I have some modifications to mandoc for generating syntax highlighted html pages)

* Clone the `apropos_replacement` repository from my github and checkout the
`merge_netbsd_linux` branch. On linux `make -f Makefile.linux`, on NetBSD run `make`
to compile it. Run `make install` to install the binaries or just copy the `apropos` binary to `/usr/bin`)

* To generate HTML format man pages and the apropos database, run updater.py in man-page-updater directory.

* Run gunicorn to serve the flask app, with something like:
`gunicorn --workers 2 --bind unix:apropos_web.sock -m 500 --timeout 120 wsgi:app`
(Consider making it an rc/init script to start it automatically on server startup).
You can either make gunicorn serve the site directly, or setup a proxy with Nginx.

* In case of issues, look into the config.py file, to see if any path is wrong for your
system. Also, check the apropos_wsgi.log to see any exceptions from the flask application.
