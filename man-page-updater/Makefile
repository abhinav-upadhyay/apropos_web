# Do "make screen" first, if you want to protect already installed,
# more up-to-date manual pages than the ones included in this package.
# Do "make install" to copy the pages to their destination.
# Do "make gz" or "make bz2" first if you use compressed source pages.

DESTDIR=
prefix?=/usr
MANDIR=$(prefix)/share/man

GZIP=gzip -9
BZIP2=bzip2 -9

all: screen remove install

allgz: gz all

allbz: bz2 all

screen:
	-mkdir not_installed
	for i in man?p/*; do \
		if [ $(MANDIR)/"$$i" -nt "$$i" ]; then \
			cmp -s $(MANDIR)/"$$i" "$$i" > /dev/null 2>&1; \
			if [ "$$?" != 0 ]; then mv "$$i" not_installed; fi; \
		fi; \
	done

remove:
	for i in man?p/*; do \
		rm -f $(MANDIR)/"$$i" $(MANDIR)/"$$i".gz $(MANDIR)/"$$i".bz2; \
	done

gz:
	for i in man?p; do $(GZIP) "$$i"/*; done

bz2:
	for i in man?p; do $(BZIP2) "$$i"/*; done

# Use with
#  make HTDIR=/some/dir HTOPTS=whatever html
# The sed removes the lines "Content-type: text/html\n\n"
html:
	@if [ x$(HTDIR) = x ]; then echo "You must set HTDIR."; else \
	newdirname=`echo $$i | sed s/man/html/`; \
	for i in man?; do \
		[ -d $(HTDIR)/"$$newdirname" ] || mkdir -p $(HTDIR)/"$$newdirname"; \
		find "$$i/" -type f | while read f; do \
		    dir=`dirname $$f`; \
			dir=`echo $$dir | sed s/man/html/`; \
			[ -d $(HTDIR)/$$dir ] || mkdir -p $(HTDIR)/$$dir ]; \
			( mandoc -Ios=$(OS) -Thtml -O style=/static/mandoc.css,man=../%S/%N $$f) > \
			$(HTDIR)/"$$dir"/`basename $$f`.html; \
		done; \
	done; fi

install:
	for i in man?p; do \
		install -d -m 755 $(DESTDIR)$(MANDIR)/"$$i" || exit $$?; \
		install -m 644 "$$i"/* $(DESTDIR)$(MANDIR)/"$$i" || exit $$?; \
	done; \

# someone might also want to look at /var/catman/cat2 or so ...
# a problem is that the location of cat pages varies a lot
