import json
import shlex
import subprocess
import time
from urlparse import urlparse
from flask import Flask, url_for, render_template, jsonify
from flask import request
from flask import Response
from flask import redirect
from flask import make_response
from werkzeug.contrib.fixers import ProxyFix
from lrupy.lrupy import LRUCache
from . import apropos_db_logger
from . import config
from . import logger

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
caches = {}
_logger = logger.get_logger()
dblogger = apropos_db_logger.AproposDBLogger()


@app.route('/')
@app.route('/netbsd/')
def posix_index():
    return dist_index('netbsd')

@app.route('/linux/')
def linux_index():
    return dist_index('linux')

@app.route('/posix/')
def netbsd_index():
    return dist_index('posix')

@app.route('/wvc')
def wvc():
    netbsd_logo_url = url_for('static', filename='images/netbsd.png')
    action_type = request.args.get('action')
    action ='/wvc'
    if action_type == 'bow':
        binfile = config.BOW_FILE
    else:
        binfile = config.SGRAM_FILE 
    search_term = request.args.get('term')
    if search_term is None:
        return render_template('words.html', results=[], action=action, netbsd_logo_url=netbsd_logo_url)
    cmd = config.DISTANCE_PATH + ' ' + binfile + ' ' + search_term
    distance_proc = subprocess.Popen(cmd.split(), stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    out,err = distance_proc.communicate()
    if distance_proc.returncode != 0:
        _logger.exception('Failed to get autocomplete data: %s', err)
    similar_words = []
    for line in out.split('\n'):
        similar_words.append(line)
    return render_template('words.html', results=similar_words, action=action, netbsd_logo_url=netbsd_logo_url)


def dist_index(dist):
    netbsd_logo_url = url_for('static', filename='images/netbsd.png')
    if dist not in config.DB_PATHS and dist != 'favicon.ico':
        return redirect(url_for('search'))
    ip = request.remote_addr
    user_agent = request.user_agent
    platform = user_agent.platform
    browser = user_agent.browser
    version = user_agent.version
    language = user_agent.language
    referrer = request.referrer
    dblogger.log_page_visit(1, ip, platform, browser, version, language, referrer,
                            int(time.time()), user_agent.string, dist)
    return render_template('index.html',
                           netbsd_logo_url=netbsd_logo_url)

@app.route("/man/<dist>/<section>/<name>")
def manpage(dist, section, name):
    return manpage_arch(dist, section, None, name)

@app.route("/man/<dist>/<section>/<arch>/<name>")
def manpage_arch(dist, section, arch, name):
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
               language, referrer, int(time.time()), user_agent.string, dist)

    if arch is not None:
        path = '/static/man_pages/' + dist + '/html' + section + '/' + arch + '/' + name + '.html'
    else:
        path = '/static/man_pages/' + dist + '/html' + section + '/' + name + '.html'
    response = make_response()
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['Content-Type'] = 'text/html'
    response.headers['X-Accel-Redirect'] = path
    return response

@app.route("/<dist>/search/")
@app.route("/<dist>/search")
def dist_specific_search(dist):
    netbsd_logo_url = url_for('static', filename='images/netbsd.png')
    if dist is None or dist == '':
        dist = 'netbsd'
    db_path = config.DB_PATHS.get(dist)
    if db_path is None:
        #TODO show message about OS not supported
        return redirect(url_for('search'))

    query = request.args.get('q')
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
        _log_query(query, previous_query, ip, platform, browser, version,
                  language, referrer, user_agent.string, dist)

    dist_results_cache = caches.get(dist)
    if dist_results_cache is None:
        dist_results_cache = LRUCache(config.DEFAULT_CACHE_SIZE)
        caches[dist] = dist_results_cache

    results = dist_results_cache.get(query) #TODO avoid looking up the cache when it is newly created
    suggestion = None
    if results is None:
        results = _search(query, db_path)
        _logger.debug(results)
        if results is None:
            return render_template('no_results.html', query=query, netbsd_logo_url=netbsd_logo_url)
        error = results.get('error')
        resultset = results.get('results')
        if error is not None:
            if error.get('category') == 'spell':
                suggestion = error.get('suggestion')
        if (resultset is None or len(resultset) == 0) and suggestion is None:
            return render_template('no_results.html', query=query, netbsd_logo_url=netbsd_logo_url)
        elif (resultset is None or len(resultset) == 0) and suggestion is not None:
            results = _search(suggestion, db_path)
            resultset = results.get('results')
            if resultset is None or len(resultset) == 0:
                return render_template('no_results.html', query=query, netbsd_logo_url=netbsd_logo_url)
            dist_results_cache.add(suggestion, results)
            query = suggestion
    else:
        resultset = results.get('results')

    start_index = page * 10
    end_index = page * 10 + 10
    next_page = False
    if len(resultset) > end_index:
        next_page = True
    results_list = resultset[start_index: end_index]
    return render_template('results.html', dist=dist, results=results_list, query=query,
                           page=page, next_page=next_page, suggestion=suggestion,
                           netbsd_logo_url=netbsd_logo_url)


@app.route("/search/")
@app.route("/search")
def search():
    return dist_specific_search('netbsd')

def _log_query(query, previous_query, ip, platform, browser, version, language, referrer, useragent, dist):
    dblogger.log_query(query, previous_query, ip, platform, browser, version,
                       language, referrer, int(time.time()), useragent, dist)

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
               language, referrer, click_time, useragent, dist):
    dblogger.log_click(page_name, section, rank, query, ip, platform, browser, version,
                       language, referrer, click_time, useragent, dist)

def _search(query, db_path=None):
    command = config.APROPOS_PATH + ' -j %s' % query.replace('-', '')
    if db_path is not None:
        command += ' -d %s' % db_path

    args = shlex.split(command)
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
    app.run()
