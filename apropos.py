import json
import subprocess
import time
from urlparse import urlparse
from flask import Flask, url_for, render_template, send_from_directory
from flask import request
from lrupy import LRUCache
from .apropos_db_logger import AproposDBLogger
from . import logger

app = Flask(__name__)
cache = LRUCache(10240)
_logger = logger.get_logger()
dblogger = AproposDBLogger()

@app.route("/")
def index():
    return render_template('index.html',
            netbsd_logo_url=url_for('static', filename='images/netbsd.png'))

@app.route("/res")
def get_results():
    return render_template('results.html',
            netbsd_logo_url=url_for('static', filename='images/netbsd.png'))

@app.route("/man/<os>/<section>/<name>")
def manpage(os, section, name):
    rank = request.args.get('r')
    query = request.args.get('q')
    ip = request.remote_addr
    user_agent = request.user_agent
    platform = user_agent.platform
    browser = user_agent.browser
    version = user_agent.version
    language = user_agent.language
    referrer = request.referrer
    previous_query = _get_previous_query(referrer)
    _log_click(name, section, rank, query, ip, platform, browser, version,
            language, referrer, time.time())
    path = 'man_pages/' + os + '/html' + section + '/' + name + '.html'
    return send_from_directory('static', path)

@app.route("/search")
def search():
    query = request.args.get('q')
    page = request.args.get('p', 0)
    try:
        page = int(page)
    except ValueError:
        page = 0

    if page == 0:
        ip = request.remote_addr
        user_agent = request.user_agent
        platform = user_agent.platform
        browser = user_agent.browser
        version = user_agent.version
        language = user_agent.language
        referrer = request.referrer
        previous_query = _get_previous_query(referrer)
        _log_query(query, previous_query, ip, platform, browser, version, language, referrer)

    results = cache.get(query)
    if results is None:
        results = _search(query)
        if results is None:
            #todo handle this
            pass
        elif len(results) == 0:
            #todo handle this
            pass
        cache.add(query, results)
    if results is not None:
        results = results[page * 10: page * 10 + 10]
    return render_template('results.html', results=results, query=query, page=page,
                           netbsd_logo_url=url_for('static', filename='images/netbsd.png'))

def _log_query(query, previous_query, ip, platform, browser, version, language, referrer):
    dblogger.log_query(query, previous_query, ip, platform, browser, version,
                       language, referrer, time.time())

def _get_previous_query(referrer):
    if referrer is None or referrer == '':
        return None

    referrer_url = urlparse(referrer)
    referrer_query_string = referrer_url.query
    if referrer_query_string != '':
        query_parts = referrer_query_string.split('&')
        for query in query_parts:
            param, value = query.split('=')
            if param == 'q':
                return value
    return None

def _log_click(page_name, section, rank, query, ip, platform, browser, version,
               language, referrer, click_time):
    dblogger.log_click(page_name, section, rank, query, ip, platform, browser, version,
                       language, referrer, click_time)

def _search(query):
    command = '/home/abhinav/dev/apropos_replacement/apropos -j %s' % query
    args = command.split()
    proc = subprocess.Popen(args,
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    out, err = proc.communicate()
    if proc.returncode != 0:
        _logger.error('apropos returned error: %s', err)
        return None
    if out == '':
        out = '[]'
    try:
        return json.loads(out.replace('\n', '').replace('\t', '').replace('\\', '\\\\'))
    except Exception:
        _logger.exception('Failed to parse JSON output: %s', out)
        return None

if __name__ == '__main__':
    app.run(debug=True)
