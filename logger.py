import logging
import logging.handlers

def get_logger(log_level=logging.INFO):
    logger = logging.getLogger(name='apropos_wsgi')
    logger.setLevel(log_level)
    handler = logging.handlers.RotatingFileHandler(
        filename='apropos_wsgi.log',
        maxBytes=10*1024*1024,
        backupCount=30
        )
    logger.addHandler(handler)
    return logger
