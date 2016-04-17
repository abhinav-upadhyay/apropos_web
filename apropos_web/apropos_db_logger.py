import sqlite3
from threading import Thread
from . import config
from . import logger

class AproposDBLogger(object):

    def __init__(self):
        self.logger = logger.get_logger()

    def log_page_visit(self, page_id, ip, platform, browser, version, language, referrer, visit_time, dist='netbsd'):
        t = Thread(target=self._log_page_visit, args=(page_id, ip, platform, browser,
            version, language, visit_time, dist))
        t.setDaemon(True)
        t.start()

    def log_query(self, query, previous_query, ip, platform, browser, version,
            language, referrer, query_time, dist='netbsd'):
        t = Thread(target=self._log_query, args=(query, previous_query, ip,
            platform, browser, version, language, referrer, query_time, dist))
        t.setDaemon(True)
        t.start()

    def log_click(self, page_name, section, rank, query, ip, platform, browser,
            version, language, referrer, click_time, dist='netbsd'):
        t = Thread(target=self._log_click, args=(page_name, section, rank, query, ip,
            platform, browser, version, language, referrer, click_time, dist))
        t.setDaemon(True)
        t.start()

    def _log_page_visit(self, page_id, ip, platform, browser, version, language, visit_time, dist):
        conn = self.get_connection()
        try:
            with conn:
                conn.execute('''INSERT INTO page_visit_log (dist, page_id, ip, platform, browser,
                version, language, visit_time) values (?,?,?,?,?,?,?,?)''',
                (dist, page_id, ip, platform, browser, version, language, visit_time))
        except Exception:
            self.logger.exception('''Failed to log page visit with values:
            dist: %s, page_id: %d, ip: %s, platform: %s, browser: %s, version:%s, language:%s,
            visit_time: %d''', dist, page_id, ip, platform, browser, version, language,
            visit_time)



    def _log_click(self, page_name, section, rank, query, ip, platform, browser, version,
            language, referrer, click_time, dist):
        conn = self.get_connection()
        try:
            with conn:
                conn.execute('''INSERT INTO CLICK_LOG (dist, page_name, section, rank, query,
                             ip, platform, browser, version, language, referrer,
                             click_time) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)''',
                             (dist, page_name, section, rank, query, ip, platform, browser, version,
                             language, referrer, click_time))
        except Exception:
            self.logger.exception('''Failed to log click with values:
                                  dist: %s, page_name: %s, rank: %s, query: %s, ip: %s, platform: %s,
                                  browser: %s, version: %s, language: %s, referrer: %s,
                                  click_time: %s''', dist, page_name, rank, query, ip, platform,
                                  browser, version, language, referrer, click_time)

    def _log_query(self, query, previous_query, ip, platform, browser, version,
                   language, referrer, query_time, dist='netbsd'):
        conn = self.get_connection()
        try:
            with conn:
                conn.execute('''INSERT INTO QUERY_LOG (dist, query, previous_query, ip,
                             platform, browser, version, language, referrer,
                             query_time) VALUES (?,?,?,?,?,?,?,?,?,?)''',
                             (dist, query, previous_query, ip, platform, browser, version,
                             language, referrer, query_time))
        except Exception:
            self.logger.exception('''Failed to log query with values: dist: %s, query: %s
                                  previous_query: %s, ip: %s, platform: %s, browser: %s,
                                  version: %s, language: %s, referrer: %s, query_time: %s''',
                                  dist, query, previous_query, ip, platform, browser, version,
                                  language, referrer, query_time)

    def get_connection(self):
        return sqlite3.connect(config.APROPOS_WEB_DB_PATH)
