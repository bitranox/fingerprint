import argparse
from fp_files_diff_conf import fp_files_diff_conf as conf
import lib_diff_files
import lib_helper_functions
import logging
import os
import sys

logger = logging.getLogger()

def get_commandline_parameters():
    """
    >>> sys.argv.append('--fp1=./testfiles_source/fp_files_result1_difftest.csv')
    >>> sys.argv.append('--fp2=./testfiles_source/fp_files_result2_difftest.csv')
    >>> sys.argv.append('--resultfile=./testresults/fp_files_diff_1_2.csv')
    >>> sys.argv.append('--batchmode')
    >>> get_commandline_parameters()
    >>> conf.fp1_path
    './testfiles_source/fp_files_result1_difftest.csv'
    >>> conf.interactive
    False
    """
    parser = argparse.ArgumentParser(description='create fingerprint of the files under --fp_dir ')
    parser.add_argument('positional_ignored', type=str, nargs='*', help='Positional Arguments are ignored')
    parser.add_argument('--fp1', type=str, required=False, default='', help='path to the first fingerprint, e.g. c:\\results\\fp_files_result1.csv')
    parser.add_argument('--fp2', type=str, required=False, default='', help='path to the second fingerprint, e.g. c:\\results\\fp_files_result2.csv')
    parser.add_argument('--resultfile', type=str, required=False, default='', help='path to the diff file, e.g. c:\\results\\fp_files_diff_1_2.csv')
    parser.add_argument('--batchmode', dest='batchmode', default=False, action='store_true', help='no user interactions')
    args = parser.parse_args()
    conf.fp1_path = args.fp1
    conf.fp2_path = args.fp2
    conf.fp_result_filename = args.resultfile
    conf.interactive = not args.batchmode


def main():
    """

    >>> import lib_doctest
    >>> sys.argv.append('--fp1=./testfiles_source/fp_files_result1_difftest.csv')
    >>> sys.argv.append('--fp2=./testfiles_source/fp_files_result2_difftest.csv')
    >>> sys.argv.append('--resultfile=./testresults/fp_files_diff_1_2.csv')
    >>> sys.argv.append('--batchmode')
    >>> get_commandline_parameters()
    >>> logger.level=logging.ERROR
    >>> main()  # +ELLIPSIS, +NORMALIZE_WHITESPACE


    """

    lib_helper_functions.config_console_logger()
    logger.info('create file fingerprint diff {}'.format(conf.version))

    conf.fp1_path = check_fp_file(f_input_file=conf.fp1_path, file_number=1)
    conf.fp2_path = check_fp_file(f_input_file=conf.fp2_path, file_number=2)
    check_fp_result_filename()

    conf.logfile_fullpath = lib_helper_functions.strip_extension(conf.fp_result_filename) + '.log'
    lib_helper_functions.setup_file_logging(logfile_fullpath=conf.logfile_fullpath)

    logger.info('fingerprint_1     : {}'.format(conf.fp1_path))
    logger.info('fingerprint_2     : {}'.format(conf.fp2_path))
    logger.info('results filename  : {}'.format(conf.fp_result_filename))

    with lib_diff_files.FileDiff() as file_diff:
            file_diff.create_diff_file()

    logger.info('Finished\n\n')
    lib_helper_functions.logger_flush_all_handlers()
    if conf.interactive:
        input('enter for exit, check the logfile')

def check_fp_result_filename(test_input:str= ''):
    """
    >>> conf.interactive = False
    >>> conf.f_output='./testresults/fp_files_diff_1_2.csv'
    >>> check_f_output()

    >>> conf.f_output='x:/testresults/fp_files_result_test'
    >>> check_f_output()  # +ELLIPSIS, +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
        ...
    SystemExit: 1
    >>> conf.interactive = True
    >>> check_f_output(test_input='./testresults/fp_files_result1.csv')

    can not write to x:/testresults/fp_files_result_test.csv, probably access rights

    """
    conf.fp_result_filename = lib_helper_functions.strip_extension(conf.fp_result_filename) + '.csv'
    while not is_fp_result_filename_ok(f_path=conf.fp_result_filename):
        if conf.interactive:
            if test_input:
                conf.fp_result_filename = test_input
            else:
                conf.fp_result_filename = input('result filename (e.g. c:\\results\\fp_files_diff_1_2.csv ): ')
            conf.fp_result_filename = lib_helper_functions.strip_extension(conf.fp_result_filename) + '.csv'
            if not is_fp_result_filename_ok(f_path=conf.fp_result_filename):
                logger.info('can not write to {}, probably access rights'.format(conf.fp_result_filename))
            else:
                break
        else:
            logger.info('can not write to {}, probably access rights'.format(conf.fp_result_filename))
            sys.exit(1)

def check_fp_file(f_input_file:str, file_number:int, test_input:str= '')->str:
    """
    >>> conf.interactive = True
    >>> check_fp_file(f_input_file='./testfiles/', file_number=1,test_input='./testfiles_source/fp_files_result1_difftest.csv')
    './testfiles_source/fp_files_result1_difftest.csv'

    >>> conf.interactive = False
    >>> check_fp_file(f_input_file='./testfiles/', file_number=1)  # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
    ...
    SystemExit: 1

    >>> conf.interactive = False
    >>> check_fp_file(f_input_file='./testfiles_source/fp_files_result1_difftest.csv', file_number=1)
    './testfiles_source/fp_files_result1_difftest.csv'


    """
    while not is_fp_input_file_ok(f_input_file):
        if conf.interactive:
            if test_input:
                f_input_file = test_input
            else:
                f_input_file = input('file {} to fingerprint (e.g. c:\\test\\ ): '.format(file_number))
            if not is_fp_input_file_ok(f_input_file):
                logger.info('can not read file {}, try again'.format(f_input_file))
                lib_helper_functions.logger_flush_all_handlers()
            else:
                break
        else:
            logger.info('can not read file {}'.format(f_input_file))
            lib_helper_functions.logger_flush_all_handlers()
            sys.exit(1)
    return f_input_file

def is_fp_input_file_ok(f_path:str)->bool:
    """
    >>> is_fp_input_file_ok(f_path='./testfiles/')
    False
    >>> is_fp_input_file_ok(f_path='./testfiles')
    False
    >>> is_fp_input_file_ok(f_path='./not_exist/')
    False
    >>> is_fp_input_file_ok(f_path='./testfiles_source/fp_files_result1_difftest.csv')
    True

    """
    # noinspection PyBroadException
    try:
        if os.path.isfile(f_path):
            return True
        else:
            return False
    except Exception:
        return False

def is_fp_result_filename_ok(f_path:str)->bool:
    """
    >>> is_f_output_ok(f_path='./testresults/fp_files_result_test.csv')
    True
    >>> is_f_output_ok(f_path='./testresults/fp_files_result_test')
    True
    >>> is_f_output_ok(f_path='x:/testresults/fp_files_result_test')
    False
    """
    # noinspection PyBroadException
    try:
        lib_helper_functions.create_path_and_check_permission(f_path=f_path)
        return True
    except Exception:
        return False

def set_logfile_fullpath():
    """
    >>> conf.f_output = './testresults/fp_files_result_test'
    >>> set_logfile_fullpath()
    >>> conf.logfile_fullpath
    './testresults/fp_files_result_test.log'
    """
    conf.logfile_fullpath = lib_helper_functions.strip_extension(conf.fp_result_filename) + '.log'


if __name__ == '__main__':
    get_commandline_parameters()
    main()
