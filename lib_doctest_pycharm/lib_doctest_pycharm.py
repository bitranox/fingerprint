import doctest
import logging
import sys
logger = logging.getLogger()
logger.level = logging.INFO

class StreamHandlerAdded(object):
    streamhandler_added = False

def setup_doctest_logger_for_pycharm(log_level:int=logging.INFO):
    """
    >>> logger.info('test')     # there is no output in pycharm by default
    >>> setup_doctest_logger_for_pycharm()
    >>> logger.info('test')     # now we have the output we want
    test

    """
    if is_pytest_running() or is_docrunner_running():
        logger_add_streamhandler_to_sys_stdout()
    logger.setLevel(log_level)


def logger_add_streamhandler_to_sys_stdout():
    if not StreamHandlerAdded.streamhandler_added:
        StreamHandlerAdded.streamhandler_added = True
        stream_handler = logging.StreamHandler(stream=sys.stdout)
        stream_handler.set_name('doctest_console')
        logger.addHandler(stream_handler)


def is_docrunner_running()->bool:
    if 'docrunner.py' in sys.argv[0]:
        return True
    else:
        return False

def is_pytest_running():
    if 'pytest_runner.py' in sys.argv[0]:
        return True
    else:
        return False

def testmod():
    logger.info('starting doctest')
    doctest.testmod()


if __name__ == '__main__':
    logger.info('this is a library and not intended to run stand alone')
    doctest.testmod()
