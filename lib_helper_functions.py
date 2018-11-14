import ctypes
import datetime
from lib_fingerprint_files import *
import logging
import os
from pathlib import Path
import sys
import time
import traceback

logger = logging.getLogger()


def convert_path_to_posix(path:str)->str:
    posix_path = path.replace('\\','/')
    return posix_path

def convert_float_to_datetime(time_float:float)->datetime.datetime:
    return datetime.datetime.fromtimestamp(time_float)

def convert_datetime_to_float(time_datetime:datetime.datetime)->float:
    """
    >>> convert_datetime_to_float("2018-11-14 19:46:58.076271")
    1542221218.076271
    """
    if isinstance(time_datetime, str):
        time_datetime = datetime.datetime.strptime(time_datetime, "%Y-%m-%d %H:%M:%S.%f")
    return time.mktime(time_datetime.timetuple()) + time_datetime.microsecond / 1E6

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


def inform_if_not_run_as_admin(exit_if_not_admin:bool=False, interactive:bool=False):
    if not is_run_as_admin():
        logger.warning('this program should run with elevated rights (run as Administrator)')
        logger_flush_all_handlers()
        if interactive:
            input('Enter to Exit')
        if exit_if_not_admin:
            sys.exit(1)

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
    time.sleep(0.1)

def config_console_logger():
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    datefmt = '%y-%m-%d %H:%M:%S'
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
        datefmt = '%y-%m-%d %H:%M:%S'
        formatter = logging.Formatter('[%(asctime)s] %(levelname)-8s: %(message)s', datefmt)
        file_logger.setFormatter(formatter)
        logging.getLogger().addHandler(file_logger)

    except Exception:
        logger.error('can not configure logfile writer - probably no permission to create directory {}'.format(logfile_dir))

def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise RuntimeError('Boolean value expected.')

def strip_extension(file_fullpath:str)->str:
    """
    >>> strip_extension('./test/test.txt')
    './test/test'
    """
    file_path = os.path.dirname(file_fullpath)
    file_base = os.path.basename(file_fullpath).rsplit('.',1)[0]
    strip_file_fullpath = os.path.join(file_path, file_base).replace('\\','/')
    return strip_file_fullpath

def touch_file_create_directory(f_path:str)->bool:
    f_dir = os.path.dirname(f_path)
    try:
        if not os.path.isdir(f_dir):
            os.makedirs(f_dir, exist_ok=True)
        Path(f_path).touch()
        return True
    except Exception:
        raise RuntimeError('can not create {}, probably not enough rights'.format(f_path))
