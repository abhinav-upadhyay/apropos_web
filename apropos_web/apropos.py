import json
import subprocess
import time
from urlparse import urlparse
from flask import Flask, url_for, render_template
from flask import request
from flask import make_response
from werkzeug.contrib.fixers import ProxyFix
from lrupy.lrupy import LRUCache
from . import apropos_db_logger
from . import config
from . import logger

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
cache = LRUCache(10240)
_logger = logger.get_logger()
dblogger = apropos_db_logger.AproposDBLogger()

@app.route("/")
def index():
    ip = request.remote_addr
    user_agent = request.user_agent
    platform = user_agent.platform
    browser = user_agent.browser
    version = user_agent.version
    language = user_agent.language
    referrer = request.referrer
    dblogger.log_page_visit(1, ip, platform, browser, version, language, referrer,
                            int(time.time()))
    netbsd_logo_url = url_for('static', filename='images/netbsd.png')
    return render_template('index.html',
                           netbsd_logo_url=netbsd_logo_url)

@app.route("/man/<os>/<section>/<name>")
def manpage(os, section, name):
    '''
    Log the search query to the DB and serve the static man page
    '''

    rank = request.args.get('r')
    query = request.args.get('q')
    ip = request.remote_addr
    user_agent = request.user_agent
    platform = user_agent.platform
    browser = user_agent.browser
    version = user_agent.version
    language = user_agent.language
    referrer = request.referrer
    if query is None or query == '':
        query = _get_previous_query(referrer)
    _log_click(name, section, rank, query, ip, platform, browser, version,
               language, referrer, int(time.time()))

    path = '/static/man_pages/' + os + '/html' + section + '/' + name + '.html'
    response = make_response()
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['Content-Type'] = 'text/html'
    response.headers['X-Accel-Redirect'] = path
    return response


@app.route("/search/")
@app.route("/search")
def search():
    query = request.args.get('q')
    netbsd_logo_url = url_for('static', filename='images/netbsd.png')
    if query is None or query == '':
        return render_template('index.html', netbsd_logo_url=netbsd_logo_url)

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
    suggestion = None
    if results is None:
        results = _search(query)
        _logger.info(results)
        if results is None:
            return render_template('no_results.html', query=query, netbsd_logo_url=netbsd_logo_url)
        error = results.get('error')
        resultset = results.get('results')
        if error is not None:
            if error.get('category') == 'spell':
                suggestion = error.get('suggestion')
        if resultset is None and suggestion is None:
            return render_template('no_results.html', query=query, netbsd_logo_url=netbsd_logo_url)
        elif (resultset is None or len(resultset) == 0) and suggestion is not None:
            results = _search(suggestion)
            resultset = results.get('results')
            cache.add(suggestion, results)
            query = suggestion
        #else:
        #    cache.add(query, results)

    start_index = page * 10
    end_index = page * 10 + 10
    next_page = False
    if len(resultset) > end_index:
        next_page = True
    results_list = resultset[start_index: end_index]
    return render_template('results.html', results=results_list, query=query,
                           page=page, next_page=next_page, suggestion=suggestion,
                           netbsd_logo_url=netbsd_logo_url)

def _log_query(query, previous_query, ip, platform, browser, version, language, referrer):
    dblogger.log_query(query, previous_query, ip, platform, browser, version,
                       language, referrer, int(time.time()))

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
    command = config.APROPOS_PATH + ' -j %s' % query
    args = command.split()
    proc = subprocess.Popen(args,
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    out, err = proc.communicate()
    if proc.returncode != 0:
        _logger.error('apropos returned error: %s for query %s', err, query)
    if out is None or out == '':
        _logger.info('No results for query %s', query)
        out = '[]'
    try:
        out = filter(lambda x: x != '\n' and x != '\t' and ord(x) <= 127, out)
        return json.loads(out.replace('\\', '\\\\'))
    except Exception:
        _logger.exception('Failed to parse JSON output: %s', out)
        return None

if __name__ == '__main__':
    app.run(debug=True)
