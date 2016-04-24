# A Flask based web interface for apropos(1)

In the summer of 2011, I worked on rewriting [apropos(1)] (https://github.com/abhinav-upadhyay/apropos_replacement) utility for [NetBSD] (http://netbsd.org) as part of Google Summer of Code 2011. This project attempts to develop a web interface for it.

Unlike the traditional apropos implementations, the apropos in NetBSD does full text search and has a ranking algorithm to show the most relevant results at the top. So you could run queries like [create socket] (https://man-k.org/search?q=create+socket) or [search man pages] (https://man-k.org/search?q=search+man+pages).

It also does a basic spell check for queries and offers suggestions. For example try [make directry] (https://man-k.org/search?q=make+directry)

### See it in action here: [man-k.org] (https://man-k.org)
Currently it supports searching two distributions of man pages:
* ```NetBSD``` man pages: https://man-k.org/netbsd/ or https://man-k.org
* ```posix``` man pages: https://man-k.org/posix/
