import ctypes
from datetime import datetime
import logging
import os
import sys
from time import sleep
import traceback

logger = logging.getLogger()

def convert_path_to_posix(path:str)->str:
    posix_path = path.replace('\\','/')
    return posix_path

def convert_timestamp_to_datetime(f_timestamp:float)->datetime:
    return datetime.fromtimestamp(f_timestamp)

def is_run_as_admin()->bool:
    """
    >>> is_run_as_admin()
    """
    try:
        is_admin = os.getuid() == 0
    except AttributeError:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    return is_admin


def is_run_as_admin2() -> bool:
    if os.name == 'nt':
        # noinspection PyBroadException
        try:
            # only windows users with admin privileges can read the C:\windows\temp
            os.listdir(os.sep.join([os.environ.get('SystemRoot', 'C:\\windows'), 'temp']))
        except Exception:
            return False
        else:
            return True
    else:
        if 'SUDO_USER' in os.environ and os.geteuid() == 0:
            return True
        else:
            return False


def exit_if_not_run_as_admin():
    if not is_run_as_admin():
        logger.warning('this program needs to run with elevated rights (run as Administrator)')
        logger_flush_all_handlers()
        input('Enter to Exit')
        exit()

def log_exception_traceback(s_error:str= '', log_level:int=logging.WARNING, log_level_traceback:int=logging.DEBUG, flush_handlers:bool=False)->str:
    s_message = s_error
    if s_error:
        s_message += ' :'
    s_message += str(sys.exc_info()[1])
    logger.log(log_level, s_message)

    s_traceback:str = traceback.format_exc()
    logger.log(log_level_traceback, s_traceback)
    if flush_handlers:
        logger_flush_all_handlers()
    return s_error  # to use it as input for re-raising

def logger_flush_all_handlers():
    flush_logger = logging.getLogger()
    for handler in flush_logger.handlers:
        if hasattr(handler, 'flush'):
            handler.flush()
    sleep(0.1)

def config_console_logger():
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    datefmt = '%y-%m-%d %H:%M'
    formatter = logging.Formatter('[%(asctime)s] %(levelname)-8s: %(message)s', datefmt)
    console.setFormatter(formatter)
    logging.getLogger().addHandler(console)

def config_file_logger(logfile_fullpath:str):
    logfile_dir = os.path.dirname(logfile_fullpath)
    # noinspection PyBroadException
    try:
        if not os.path.isdir(logfile_dir):
            os.makedirs(logfile_dir, exist_ok=True)

        file_logger = logging.FileHandler(filename=logfile_fullpath, mode='w', encoding='utf-8')
        file_logger.setLevel(logging.DEBUG)
        datefmt = '%y-%m-%d %H:%M'
        formatter = logging.Formatter('[%(asctime)s] %(levelname)-8s: %(message)s', datefmt)
        file_logger.setFormatter(formatter)
        logging.getLogger().addHandler(file_logger)

    except Exception:
        logger.error('can not configure logfile writer - probably no permission to create directory {}'.format(logfile_dir))
