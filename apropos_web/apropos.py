from gensim import similarities, corpora, models
import json
import pandas as pd
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
from stemming import porter2
from . import apropos_db_logger
from . import config
from . import logger

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
caches = {}
_logger = logger.get_logger()
dblogger = apropos_db_logger.AproposDBLogger()
man_df = None
distnames = config.DB_PATHS.keys()


@app.route('/whatis')
def whatis():
    query = request.args.get('q')
    dists = request.args.getlist('dist')
    netbsd_logo_url = url_for('static', filename='images/netbsd.png')
    results = None
    selected = {}
    if query is not None and  query != '':
        if dists is None or dists == '':
            dists = distnames
        else:
            for dist in dists:
                selected[dist] = True
        results = _whatis(query, dists)

    return render_template('whatis.html', netbsd_logo_url=netbsd_logo_url,
            query='', page=0, distnames=distnames, results=results, selected=selected)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
@app.route('/<path:path>/')
def posix_index(path):
    _logger.info("Request for %s" % path)
    if path == 'words':
        return wvc()

    if path == 'search':
        return search()

    return dist_index(path)

@app.route('/words/')
def wvc():
    netbsd_logo_url = url_for('static', filename='images/netbsd.png')
    action_type = request.args.get('action')
    action ='/words/'
    if action_type == 'bow':
        binfile = config.BOW_FILE
    else:
        binfile = config.SGRAM_FILE 
    search_term = request.args.get('term')
    if search_term is None:
        return render_template('words.html', results=[], action=action, netbsd_logo_url=netbsd_logo_url)
    search_term = search_term.lower()
    cmd = config.DISTANCE_PATH + ' ' + binfile + ' ' + search_term
    distance_proc = subprocess.Popen(cmd.split(), stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    out,err = distance_proc.communicate()
    if distance_proc.returncode != 0:
        _logger.exception('Failed to get autocomplete data: %s', err)
        error = 'Please enter single word queries in singular form, like: bug, kernel, driver'
        return render_template('words.html', term=search_term, action_type=action_type, error=error,
            action=action, netbsd_logo_url=netbsd_logo_url)
    similar_words = []
    for line in out.split('\n'):
        similar_words.append(line)
    return render_template('words.html', term=search_term, action_type=action_type, results=similar_words,
            action=action, netbsd_logo_url=netbsd_logo_url)


def dist_index(dist):
    netbsd_logo_url = url_for('static', filename='images/netbsd.png')
    if dist is None or dist == '':
        dist = 'NetBSD-current'
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
                           netbsd_logo_url=netbsd_logo_url, distnames=distnames)

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
        return render_template('index.html', netbsd_logo_url=netbsd_logo_url, dist=dist, distnames=distnames)

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
            return render_template('no_results.html', query=query, netbsd_logo_url=netbsd_logo_url, dist=dist, distnames=distnames)
        error = results.get('error')
        resultset = results.get('results')
        if error is not None:
            if error.get('category') == 'spell':
                suggestion = error.get('suggestion')
        if (resultset is None or len(resultset) == 0) and suggestion is None:
            return render_template('no_results.html', query=query, netbsd_logo_url=netbsd_logo_url, dist=dist, distnames=distnames)
        elif (resultset is None or len(resultset) == 0) and suggestion is not None:
            results = _search(suggestion, db_path)
            resultset = results.get('results')
            if resultset is None or len(resultset) == 0:
                return render_template('no_results.html', query=query, netbsd_logo_url=netbsd_logo_url, dist=dist, distnames=distnames)
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
                           netbsd_logo_url=netbsd_logo_url, distnames=distnames)


@app.route("/search/")
@app.route("/search")
def search():
    dist = request.args.get('dist')
    if dist is None or dist == '':
        dist = 'NetBSD-current'
    return dist_specific_search(dist)

@app.route("/similar")
def similar():
    netbsd_logo_url = url_for('static', filename='images/netbsd.png')
    man_page_name = request.args.get('n')
    section = request.args.get('s')
    if man_page_name is None:
        return render_template('similar.html', 
                netbsd_logo_url=netbsd_logo_url)
    if man_df is None:
        man_df = pd.read_csv('man.csv', delimiter='\t')
    if section is not None and section != '':
        data = man_df[(man_df['name'] == man_page_name) & (man_df['section'] == section)]
    else:
        data = man_df[man_df['name'] == man_page_name]

    if data is None or len(data) == 0:
        data = man_page_name
    else:
        data = data.iloc[0]['data']
    dictionary =  corpora.Dictionary.load('man.dict')
    lsi_index = similarities.MatrixSimilarity.load('man.index')
    lsi_model = models.LsiModel.load('man.lsi')
    vec_bow = dictionary.doc2bow(porter2.stem(word) for word in data.lower().split())
    vec_lsi = lsi_model[vec_bow]
    sims = lsi_index[vec_lsi]
    sims = sorted(enumerate(sims), key=lambda item: -item[1])
    results = []
    duplicates = {}
    for i, prob in sims[:20]:
        result_name = man_df['name'][i]
        result_section = man_df['section'][i]
        if man_page_name == result_name and section == result_section:
            continue
        d = {}
        d['name'] = result_name
        d['section'] = result_section
        d['score'] = prob
        if duplicates.get((result_name, result_section)) is not None:
                continue
        results.append(d)
        duplicates[(result_name, result_section)] = prob
    return render_template('similar.html', results=results, name=man_page_name, section=section,
            netbsd_logo_url=netbsd_logo_url)



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
    command = config.APROPOS_PATH
    if db_path is not None:
        command += ' -d %s' % db_path
    command += ' -j %s' % query.replace('-', '')

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
        out = '{}'
    try:
        out = filter(lambda x: x != '\n' and x != '\t' and ord(x) <= 127, out)
        return json.loads(out.replace('\\', '\\\\').replace('\r\n', ''), strict=False)
    except Exception:
        _logger.exception('Failed to parse JSON output: %s', out)
        return None

def _whatis(query, dists):
    response = {}
    for dist in dists:
        command = config.WHATIS_PATH
        response[dist] = []
        db_path = config.DB_PATHS[dist]
        if db_path is None:
            continue
        command += ' -d %s %s' % (db_path, query)
        args = shlex.split(command)
        proc = subprocess.Popen(args,
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE
                                )
        out, err = proc.communicate()
        if proc.returncode != 0:
            _logger.error('whatis returned error %s for query %s for dist %s', err, query, dist)
            continue
        if out is None or out == '':
            _logger.info('No results for query %s for dist %s', query, dist)
            continue
        lines = out.splitlines()
        for line in lines:
            d = {}
            tokens = line.split('-')
            name_parts = tokens[0].split('(')
            d['name'] = name_parts[0]
            d['section'] = name_parts[1][:-2]
            d['desc'] = tokens[1]
            response[dist].append(d)
    return response

if __name__ == '__main__':
    app.run()
