import sqlite3
from threading import Thread
from . import config
from . import logger

class AproposDBLogger(object):

    def __init__(self):
        self.logger = logger.get_logger()

    def log_query(self, query, previous_query, ip, platform, browser, version,
            language, referrer, query_time):
        t = Thread(target=self._log_query, args=(query, previous_query, ip,
            platform, browser, version, language, referrer, query_time))
        t.setDaemon(True)
        t.start()

    def log_click(self, page_name, section, rank, query, ip, platform, browser,
            version, language, referrer, click_time):
        t = Thread(target=self._log_click, args=(page_name, section, rank, query, ip,
            platform, browser, version, language, referrer, click_time))
        t.setDaemon(True)
        t.start()

    def _log_click(self, page_name, section, rank, query, ip, platform, browser, version,
            language, referrer, click_time):
        conn = self.get_connection()
        try:
            with conn:
                conn.execute('''INSERT INTO CLICK_LOG (page_name, section, rank, query,
                             ip, platform, browser, version, language, referrer,
                             click_time) VALUES(?,?,?,?,?,?,?,?,?,?,?)''',
                             (page_name, section, rank, query, ip, platform, browser, version,
                             language, referrer, click_time))
        except Exception:
            self.logger.exception('''Failed to log click with values:
                                  page_name: %s, rank: %d, query: %s, ip: %s, platform: %s,
                                  browser: %s, version: %s, language: %s, referrer: %s,
                                  click_time: %s''', page_name, rank, query, ip, platform,
                                  browser, version, language, referrer, click_time)

    def _log_query(self, query, previous_query, ip, platform, browser, version,
                   language, referrer, query_time):
        conn = self.get_connection()
        try:
            with conn:
                conn.execute('''INSERT INTO QUERY_LOG (query, previous_query, ip,
                             platform, browser, version, language, referrer,
                             query_time) VALUES (?,?,?,?,?,?,?,?,?)''',
                             query, previous_query, ip, platform, browser, version,
                             language, referrer, query_time)
        except Exception:
            self.logger.exception('''Failed to log query with values: query: %s
                                  previous_query: %s, ip: %s, platform: %s, browser: %s,
                                  version: %s, language: %s, referrer: %s, query_time: %s''',
                                  query, previous_query, ip, platform, browser, version,
                                  language, referrer, query_time)

    def get_connection(self):
        return sqlite3.connect(config.APROPOS_WEB_DB_PATH)
