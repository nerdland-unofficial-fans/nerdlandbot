import logging

logging.basicConfig(filename='bot.log', level=logging.INFO)


def debug(msg, *args, **kwargs):
    print(f'DEBUG   |{msg}')
    logging.debug(msg, *args, **kwargs)

def info(msg, *args, **kwargs):
    print(f'INFO    |{msg}')
    logging.info(msg, *args, **kwargs)

def warn(msg, *args, **kwargs):
    print(f'WARNING |{msg}')
    logging.warning(msg, *args, **kwargs)

def error(msg, *args, **kwargs):
    print(f'ERROR   |{msg}')
    logging.error(msg, *args, **kwargs)

def fatal(msg, *args, **kwargs):
    print(f'FATAL   |{msg}')
    logging.fatal(msg, *args, **kwargs)
