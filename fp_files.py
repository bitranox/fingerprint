import argparse
from lib_fingerprint_files import FingerPrintFiles
from lib_helper_functions import *
import lib_doctest
import logging
import sys
import time

logger = logging.getLogger()
lib_doctest.setup_doctest_logger()

def get_commandline_parameters():
    """
    >>> sys.argv.append('--fp_files_dir=./testfiles/')
    >>> sys.argv.append('--fp_result_filename=./testresults/fp_files_result1.csv')
    >>> args = get_commandline_parameters()
    >>> args.fp_files_dir
    'test'
    """
    parser = argparse.ArgumentParser(description='create fingerprint of the files under --fp_files_dir ')
    parser.add_argument('positional_ignored', type=str, nargs='*', help='Positional Arguments are ignored')
    parser.add_argument('--fp_files_dir', type=str, required=False, default='', help='path to the directory to fingerprint, e.g. c:\\test\\')
    parser.add_argument('--fp_result_filename', type=str, required=False, default='', help='path to the result file, e.g. c:\\results\\fp_files_result1.csv')
    args = parser.parse_args()
    return args

def get_logfile_fullpath(fp_result_filename:str)->str:
    """
    >>> get_logfile_fullpath('./testresults/fp_files_result1.csv')
    './testresults/fp_files_result1.log'
    """
    logfile_fullpath = fp_result_filename.rsplit('.',1)[0] + '.log'
    return logfile_fullpath

def main(fp_files_dir:str, fp_result_filename:str):
    """
    >>> import test
    >>> timestamp = time.time()
    >>> test.create_testfiles_fingerprint_1(timestamp)
    >>> main(fp_files_dir='./testfiles/', fp_result_filename='./testresults/fp_files_result1.csv')
    >>> test.modify_testfiles_fingerprint_2(timestamp)
    >>> main(fp_files_dir='./testfiles/', fp_result_filename='./testresults/fp_files_result2.csv')
    """
    config_console_logger()
    exit_if_not_run_as_admin()
    logger.info('create files fingerprint')

    fp_files_dir = check_fp_files_dir(fp_files_dir)
    fp_result_filename = check_fp_result_filename(fp_result_filename)

    logger.info('fingerprinting directory : {}'.format(fp_files_dir))
    logger.info('results filename         : {}'.format(fp_result_filename))

    logfile_fullpath = get_logfile_fullpath(fp_result_filename)
    config_file_logger(logfile_fullpath)

    # fp_files_dir:str, fp_result_filename:str

    with FingerPrintFiles(fp_files_dir=fp_files_dir,
                          fp_result_filename=fp_result_filename) as fingerprint_files:
        fingerprint_files.create_fp()

    logger.info('Finished\n\n')
    logger_flush_all_handlers()
    input('enter for exit, check the logfile')

def check_fp_result_filename(fp_result_filename:str)->str:
    while True:
        if not fp_result_filename:
            fp_result_filename = input('result filename (e.g. c:\\results\\fingerprint1.csv ): ')
        if is_fp_result_filename_ok(fp_result_filename):
            break
        else:
            logger.info('result filename not writable, try again')
            logger_flush_all_handlers()
    return fp_result_filename

def check_fp_files_dir(fp_files_dir:str)->str:
    while True:
        if not fp_files_dir:
            fp_files_dir = input('directory to fingerprint (e.g. c:\\test\\ ): ')
        if is_fp_files_dir_ok(fp_files_dir):
            break
        else:
            logger.info('directory does not exist, try again')
            logger_flush_all_handlers()
    return fp_files_dir

def is_fp_files_dir_ok(fp_files_dir)->bool:
    # TODO
    return True

def is_fp_result_filename_ok(fp_result_filename)->bool:
    # TODO
    return True


if __name__ == '__main__':
    commandline_args = get_commandline_parameters()
    _fp_files_dir:str = commandline_args.fp_files_dir
    _fp_result_filename:str = commandline_args.fp_result_filename
    main(fp_files_dir=_fp_files_dir, fp_result_filename=_fp_result_filename)
