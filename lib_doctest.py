import logging
import sys

logger = logging.getLogger()

def setup_doctest_logger(log_level: int = logging.DEBUG):
    """

    :param log_level:
    :return:

    >>> logger.info('test')     # there is no output in pycharm by default
    >>> setup_doctest_logger()
    >>> logger.info('test')     # now we have the output we want
    test

    """
    if is_pycharm_running():
        logger_add_streamhandler_to_sys_stdout()
    logger.setLevel(log_level)

def is_pycharm_running() -> bool:
    if ('docrunner.py' in sys.argv[0]) or ('pytest_runner.py' in sys.argv[0]):
        return True
    else:
        return False

def logger_add_streamhandler_to_sys_stdout():
    stream_handler = logging.StreamHandler(stream=sys.stdout)
    logger.addHandler(stream_handler)
