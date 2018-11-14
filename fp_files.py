import argparse
from fp_files_conf import fp_files_conf as conf
import lib_fingerprint_files
import lib_helper_functions
import lib_doctest
import logging
import multiprocessing
import sys
import time

logger = logging.getLogger()
lib_doctest.setup_doctest_logger()

def get_commandline_parameters():
    """
    >>> sys.argv.append('--fp_files_dir=./testfiles/')
    >>> sys.argv.append('--fp_result_filename=./testresults/fp_files_result1.csv')
    >>> sys.argv.append('--non_interactive')
    >>> sys.argv.append('--continue_if_not_admin')
    >>> sys.argv.append('--no_file_hashing')
    >>> sys.argv.append('--no_multiprocessing')
    >>> get_commandline_parameters()
    >>> conf.fp_files_dir
    './testfiles/'
    >>> conf.interactive
    False
    >>> conf.exit_if_not_admin
    False

    """
    parser = argparse.ArgumentParser(description='create fingerprint of the files under --fp_files_dir ')
    parser.add_argument('positional_ignored', type=str, nargs='*', help='Positional Arguments are ignored')
    parser.add_argument('--fp_files_dir', type=str, required=False, default='', help='path to the directory to fingerprint, e.g. c:\\test\\')
    parser.add_argument('--fp_result_filename', type=str, required=False, default='', help='path to the result file, e.g. c:\\results\\fp_files_result1.csv')
    parser.add_argument('--non_interactive', dest='non_interactive', default=False, action='store_true')
    parser.add_argument('--continue_if_not_admin', dest='continue_if_not_admin', default=False, action='store_true')
    parser.add_argument('--no_file_hashing', dest='no_file_hashing', default=False, action='store_true')
    parser.add_argument('--no_multiprocessing', dest='no_multiprocessing', default=False, action='store_true')

    args = parser.parse_args()
    conf.fp_files_dir = args.fp_files_dir
    conf.fp_result_filename = args.fp_result_filename
    conf.interactive = not args.non_interactive
    conf.exit_if_not_admin = not args.continue_if_not_admin
    conf.hash_files = not args.no_file_hashing
    conf.multiprocessing = not args.no_multiprocessing

def main():
    """
    >>> import test
    >>> timestamp = time.time()
    >>> test.create_testfiles_fingerprint_1(timestamp)
    >>> sys.argv.append('--fp_files_dir=./testfiles/')
    >>> sys.argv.append('--fp_result_filename=./testresults/fp_files_result1.csv')
    >>> sys.argv.append('--non_interactive')
    >>> sys.argv.append('--continue_if_not_admin')
    >>> get_commandline_parameters()
    >>> logger.level=logging.ERROR
    >>> main()  # +ELLIPSIS, +NORMALIZE_WHITESPACE

    >>> test.modify_testfiles_fingerprint_2(timestamp)
    >>> sys.argv.append('--fp_result_filename=./testresults/fp_files_result2.csv')
    >>> get_commandline_parameters()
    >>> logger.level=logging.ERROR
    >>> main()  # +ELLIPSIS, +NORMALIZE_WHITESPACE

    >>> sys.argv.append('--no_multiprocessing')
    >>> get_commandline_parameters()
    >>> logger.level=logging.ERROR
    >>> main()  # +ELLIPSIS, +NORMALIZE_WHITESPACE

    """

    lib_helper_functions.config_console_logger()
    lib_helper_functions.inform_if_not_run_as_admin(exit_if_not_admin=conf.exit_if_not_admin, interactive=conf.interactive)
    logger.info('create files fingerprint')

    check_fp_files_dir()
    check_fp_result_filename()

    logger.info('fingerprinting directory : {}'.format(conf.fp_files_dir))
    logger.info('results filename         : {}'.format(conf.fp_result_filename))

    set_logfile_fullpath()
    lib_helper_functions.config_file_logger(logfile_fullpath=conf.logfile_fullpath)

    with lib_fingerprint_files.FingerPrintFiles() as fingerprint_files:
        if conf.multiprocessing:                # test c:\windows : 66 seconds
            fingerprint_files.create_fp_mp()
        else:
            fingerprint_files.create_fp()       # test c:\windows : 124 seconds

    logger.info('Finished\n\n')
    lib_helper_functions.logger_flush_all_handlers()
    if conf.interactive:
        input('enter for exit, check the logfile')

def check_fp_result_filename(test_input:str= ''):
    """
    >>> conf.interactive = False
    >>> conf.fp_result_filename='./testresults/fp_files_result1.csv'
    >>> check_fp_result_filename()

    >>> conf.fp_result_filename='x:/testresults/fp_files_result_test'
    >>> check_fp_result_filename()  # +ELLIPSIS, +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
        ...
    SystemExit: None
    >>> conf.interactive = True
    >>> check_fp_result_filename(test_input='./testresults/fp_files_result1.csv')

    can not write to x:/testresults/fp_files_result_test.csv, probably access rights

    """
    conf.fp_result_filename = lib_helper_functions.strip_extension(conf.fp_result_filename) + '.csv'
    while not is_fp_result_filename_ok():
        if conf.interactive:
            if test_input:
                conf.fp_result_filename = test_input
            else:
                conf.fp_result_filename = input('result filename (e.g. c:\\results\\fingerprint1.csv ): ')
            conf.fp_result_filename = lib_helper_functions.strip_extension(conf.fp_result_filename) + '.csv'
            if not is_fp_result_filename_ok():
                logger.info('can not write to {}, probably access rights'.format(conf.fp_result_filename))
            else:
                break
        else:
            logger.info('can not write to {}, probably access rights'.format(conf.fp_result_filename))
            exit()

def check_fp_files_dir(test_input:str= ''):
    """
    >>> conf.interactive = False
    >>> conf.fp_files_dir = './testfiles/'
    >>> check_fp_files_dir()
    >>> conf.fp_files_dir = './not_exist/'
    >>> check_fp_files_dir()  # +ELLIPSIS, +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
        ...
    SystemExit: None
    >>> conf.interactive = True
    >>> check_fp_files_dir(test_input='./testfiles/')  # +ELLIPSIS, +NORMALIZE_WHITESPACE

    can not read directory ./not_exist/

    """
    while not is_fp_files_dir_ok():
        if conf.interactive:
            if test_input:
                conf.fp_files_dir = test_input
            else:
                conf.fp_files_dir = input('directory to fingerprint (e.g. c:\\test\\ ): ')
            if not is_fp_files_dir_ok():
                logger.info('can not read directory {}, try again'.format(conf.fp_files_dir))
                lib_helper_functions.logger_flush_all_handlers()
            else:
                break
        else:
            logger.info('can not read directory {}'.format(conf.fp_files_dir))
            lib_helper_functions.logger_flush_all_handlers()
            exit()

def is_fp_files_dir_ok()->bool:
    """
    >>> conf.fp_files_dir = './testfiles/'
    >>> is_fp_files_dir_ok()
    True
    >>> conf.fp_files_dir = './testfiles'
    >>> is_fp_files_dir_ok()
    True
    >>> conf.fp_files_dir = './not_exist/'
    >>> is_fp_files_dir_ok()
    False
    """
    # noinspection PyBroadException
    try:
        lib_fingerprint_files.format_fp_files_dir()
        return True
    except Exception:
        return False

def is_fp_result_filename_ok()->bool:
    """
    >>> conf.fp_result_filename = './testresults/fp_files_result_test.csv'
    >>> is_fp_result_filename_ok()
    True
    >>> conf.fp_result_filename = './testresults/fp_files_result_test'
    >>> is_fp_result_filename_ok()
    True
    >>> conf.fp_result_filename = 'x:/testresults/fp_files_result_test'
    >>> is_fp_result_filename_ok()
    False
    """
    # noinspection PyBroadException
    try:
        lib_fingerprint_files.create_check_fp_result_dir()
        return True
    except Exception:
        return False

def set_logfile_fullpath():
    """
    >>> conf.fp_result_filename = './testresults/fp_files_result_test'
    >>> set_logfile_fullpath()
    >>> conf.logfile_fullpath
    './testresults/fp_files_result_test.log'
    """
    conf.logfile_fullpath = lib_helper_functions.strip_extension(conf.fp_result_filename) + '.log'


if __name__ == '__main__':
    # Hack for multiprocessing.freeze_support() to work from a
    # setuptools-generated entry point.
    multiprocessing.freeze_support()
    get_commandline_parameters()
    main()
