import argparse
import click
from fp_conf import fp_conf, fp_files_conf, fp_diff_files_conf, fp_reg_conf
import lib_diff_files
import lib_fingerprint_files
import lib_fingerprint_registry
import lib_helper_functions
import logging
import multiprocessing
import os
import sys
import time

logger = logging.getLogger()
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version=fp_conf.version)
def fp():
    pass

@fp.command()
@click.option('--fp_dir', type=click.Path(), default='', help='path to the directory to fingerprint, e.g. c:\\test\\')
@click.option('--f_output', type=click.Path(), default='', help='path to the output file, e.g. c:\\results\\fp_files_result1.csv')
@click.option('--batchmode', is_flag=True, help='no user interactions')
@click.option('--no_admin', is_flag=True, help='do not check for admin rights, not recommended')
@click.option('--no_hashing', is_flag=True, help='do not calculate file hashes, not recommended')
@click.option('--no_mp', is_flag=True, help='no multiprocessing - preserves ordering of files in the result')
def files(**kwargs):
    """
    (fp files --help for more help on that command)
    """

    """
    >>> import test
    >>> import lib_doctest
    >>> lib_doctest.setup_doctest_logger()
    >>> timestamp = time.time()
    >>> test.create_testfiles_fingerprint_1(timestamp)
    >>> kwargs=dict()
    >>> kwargs['fp_dir'] = './testfiles/'
    >>> kwargs['f_output'] = './testresults/fp_files_result1.csv'
    >>> kwargs['batchmode'] = True
    >>> kwargs['no_admin'] = True
    >>> kwargs['no_mp'] = False
    >>> kwargs['no_hashing'] = False

    >>> logger.level=logging.ERROR
    >>> files(**kwargs)  # +ELLIPSIS, +NORMALIZE_WHITESPACE

    >>> test.modify_testfiles_fingerprint_2(timestamp)
    >>> kwargs['f_output'] = './testresults/fp_files_result2.csv'
    >>> logger.level=logging.ERROR
    >>> files()  # +ELLIPSIS, +NORMALIZE_WHITESPACE

    >>> kwargs['no_mp'] = True
    >>> logger.level=logging.ERROR
    >>> files()  # +ELLIPSIS, +NORMALIZE_WHITESPACE

    >>> kwargs['no_hashing'] = True
    >>> logger.level=logging.ERROR
    >>> files()  # +ELLIPSIS, +NORMALIZE_WHITESPACE


    """
    files_save_commandline_options_to_conf(**kwargs)
    lib_helper_functions.config_console_logger()
    lib_helper_functions.inform_if_not_run_as_admin(exit_if_not_admin=fp_files_conf.exit_if_not_admin, interactive=fp_conf.interactive)
    logger.info('create files fingerprint {}'.format(fp_conf.version))
    check_or_request_fp_dir()
    check_or_request_f_output()
    lib_helper_functions.SetupFileLogging(f_output=fp_conf.f_output)
    log_files_parameter()
    with lib_fingerprint_files.FingerPrintFiles() as fingerprint_files:
        if fp_files_conf.multiprocessing:                # test c:\windows : 66 seconds
            fingerprint_files.create_fp_mp()
        else:
            fingerprint_files.create_fp()       # test c:\windows : 124 seconds
    exit_message()

@fp.command()
@click.option('--fp1', type=click.Path(), default='', help='path to the first fingerprint, e.g. c:\\results\\fp_files_result1.csv')
@click.option('--fp2', type=click.Path(), default='', help='path to the second fingerprint, e.g. c:\\results\\fp_files_result2.csv')
@click.option('--f_output', type=click.Path(), default='', help='path to the diff file, e.g. c:\\results\\fp_files_diff_1_2.csv')
@click.option('--batchmode', is_flag=True, help='no user interactions')
def files_diff(**kwargs):
    """
    (fp files_diff --help for more help on that command)
    """

    """
    >>> import lib_doctest
    >>> kwargs = dict()
    >>> kwargs['fp1'] = './testfiles_source/fp_files_result1_difftest.csv'
    >>> kwargs['fp2'] = './testfiles_source/fp_files_result2_difftest.csv'
    >>> kwargs['f_output'] = './testresults/fp_files_diff_1_2.csv'
    >>> kwargs['batchmode'] = True
    >>> logger.level=logging.ERROR
    >>> files_diff(**kwargs)  # +ELLIPSIS, +NORMALIZE_WHITESPACE

    """

    diff_files_save_commandline_options_to_conf(**kwargs)
    lib_helper_functions.config_console_logger()
    logger.info('create file fingerprint diff {}'.format(fp_conf.version))

    fp_diff_files_conf.fp1_path = check_or_request_fp_file(f_input_file=fp_diff_files_conf.fp1_path, file_number=1)
    fp_diff_files_conf.fp2_path = check_or_request_fp_file(f_input_file=fp_diff_files_conf.fp2_path, file_number=2)
    check_or_request_f_output()
    lib_helper_functions.SetupFileLogging(f_output=fp_conf.f_output)
    log_files_diff_parameter()
    with lib_diff_files.FileDiff() as file_diff:
        file_diff.create_diff_file()
    exit_message()

@fp.command()
@click.option('--f_output', type=click.Path(), default='', help='path to the output file, e.g. c:\\results\\fp_registry_result1.csv')
@click.option('--field_length_limit', type=click.INT, default=32767, help='data from registry, default set to maximum length of a cell in excel (32767) - but we can support much longer fields')
@click.option('--reg_save_additional_parameters', default='', help='optional reg save parameters, e.g. "/reg:64" or "/reg:32"')
@click.option('--do_not_delete_hive_copies', is_flag=True, help='do not delete the registry hive files')
@click.option('--no_admin', is_flag=True, help='do not check for admin rights, not recommended')
@click.option('--batchmode', is_flag=True, help='no user interactions')
def reg(**kwargs):
    """
    (fp reg --help for more help on that command)
    """

    reg_save_commandline_options_to_conf(**kwargs)
    lib_helper_functions.config_console_logger()
    lib_helper_functions.inform_if_not_run_as_admin(exit_if_not_admin=fp_reg_conf.exit_if_not_admin, interactive=fp_conf.interactive)
    logger.info('create registry fingerprint {}'.format(fp_conf.version))
    check_or_request_f_output(fp_conf.f_output)
    lib_helper_functions.SetupFileLogging(f_output=fp_conf.f_output)
    log_reg_parameter()
    with lib_fingerprint_registry.FingerPrintRegistry() as fingerprint_registry:
        fingerprint_registry.create_fingerprint_registry()
    exit_message()


def files_save_commandline_options_to_conf(**kwargs):
    save_common_parameters_to_conf(**kwargs)
    fp_files_conf.fp_dir = kwargs['fp_dir']
    fp_files_conf.exit_if_not_admin = not kwargs['no_admin']
    fp_files_conf.hash_files = not kwargs['no_hashing']
    fp_files_conf.multiprocessing = not kwargs['no_mp']

def diff_files_save_commandline_options_to_conf(**kwargs):
    save_common_parameters_to_conf(**kwargs)
    fp_diff_files_conf.fp1_path = kwargs['fp1']
    fp_diff_files_conf.fp2_path = kwargs['fp2']

def reg_save_commandline_options_to_conf(**kwargs):
    save_common_parameters_to_conf(**kwargs)
    fp_reg_conf.field_length_limit = kwargs['field_length_limit']
    fp_reg_conf.reg_save_additional_parameters = kwargs['reg_save_additional_parameters']
    fp_reg_conf.delete_hive_copies = not kwargs['do_not_delete_hive_copies']
    fp_reg_conf.exit_if_not_admin = not kwargs['no_admin']

def save_common_parameters_to_conf(**kwargs):
    fp_conf.f_output = kwargs['f_output']
    fp_conf.interactive = not kwargs['batchmode']

def check_or_request_fp_file(f_input_file:str, file_number:int, test_input:str= '')->str:
    """
    >>> fp_conf.interactive = True
    >>> check_or_request_fp_file(f_input_file='./testfiles/', file_number=1,test_input='./testfiles_source/fp_files_result1_difftest.csv')
    './testfiles_source/fp_files_result1_difftest.csv'

    >>> fp_conf.interactive = False
    >>> check_or_request_fp_file(f_input_file='./testfiles/', file_number=1)  # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
    ...
    SystemExit: 1

    >>> fp_conf.interactive = False
    >>> check_or_request_fp_file(f_input_file='./testfiles_source/fp_files_result1_difftest.csv', file_number=1)
    './testfiles_source/fp_files_result1_difftest.csv'


    """
    while not is_fp_input_file_ok(f_input_file):
        if fp_conf.interactive:
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

def check_or_request_f_output(test_input:str= ''):
    """
    >>> fp_conf.interactive = False
    >>> fp_conf.f_output = './testresults/fp_files_result1.csv'
    >>> check_or_request_f_output()

    >>> fp_conf.f_output = 'x:/testresults/fp_files_result_test'
    >>> check_or_request_f_output()  # +ELLIPSIS, +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
        ...
    SystemExit: 1
    >>> fp_conf.interactive = True
    >>> fp_conf.f_output = 'x:/testresults/fp_files_result_test'
    >>> check_or_request_f_output(test_input='./testresults/fp_files_result1.csv')

    """
    fp_conf.f_output = lib_helper_functions.strip_extension(fp_conf.f_output) + '.csv'
    while not is_f_output_ok(f_path=fp_conf.f_output):
        if fp_conf.interactive:
            if test_input:
                fp_conf.f_output = test_input
            else:
                fp_conf.f_output = input('result filename (e.g. c:\\results\\<f_out>.csv ): ')
                fp_conf.f_output = lib_helper_functions.strip_extension(fp_conf.f_output) + '.csv'
            if not is_f_output_ok(f_path=fp_conf.f_output):
                logger.info('can not write to {}, probably access rights'.format(fp_conf.f_output))
            else:
                break
        else:
            logger.info('can not write to {}, probably access rights'.format(fp_conf.f_output))
            sys.exit(1)

def check_or_request_fp_dir(test_input:str= ''):
    """
    >>> import test
    >>> import lib_doctest
    >>> lib_doctest.setup_doctest_logger()
    >>> timestamp = time.time()
    >>> test.create_testfiles_fingerprint_1(timestamp)

    >>> fp_conf.interactive = False
    >>> fp_files_conf.fp_dir = './testfiles/'
    >>> check_or_request_fp_dir()
    >>> fp_files_conf.fp_dir = './not_exist/'
    >>> check_or_request_fp_dir()  # +ELLIPSIS, +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
        ...
    SystemExit: 1
    >>> fp_conf.interactive = True
    >>> check_or_request_fp_dir(test_input='./testfiles/')  # +ELLIPSIS, +NORMALIZE_WHITESPACE

    can not read directory ./not_exist/

    """
    while not is_fp_dir_ok():
        if fp_conf.interactive:
            if test_input:
                fp_files_conf.fp_dir = test_input
            else:
                fp_files_conf.fp_dir = input('directory to fingerprint (e.g. c:\\test\\ ): ')
            if not is_fp_dir_ok():
                logger.info('can not read directory {}, try again'.format(fp_files_conf.fp_dir))
                lib_helper_functions.logger_flush_all_handlers()
            else:
                break
        else:
            logger.info('can not read directory {}'.format(fp_files_conf.fp_dir))
            lib_helper_functions.logger_flush_all_handlers()
            sys.exit(1)

def is_fp_dir_ok()->bool:
    """
    >>> fp_files_conf.fp_dir = './testfiles/'
    >>> is_fp_dir_ok()
    True
    >>> fp_files_conf.fp_dir = './testfiles'
    >>> is_fp_dir_ok()
    True
    >>> fp_files_conf.fp_dir = './not_exist/'
    >>> is_fp_dir_ok()
    False
    """
    # noinspection PyBroadException
    try:
        lib_fingerprint_files.format_fp_files_dir()
        return True
    except Exception:
        return False

def is_f_output_ok(f_path:str)->bool:
    """
    >>> is_f_output_ok(f_path='./testresults/fp_files_result_test.csv')
    True
    >>> is_f_output_ok(f_path='./testresults/fp_files_result_test')
    True
    >>> is_f_output_ok(f_path='x:/testresults/fp_files_result_test')
    can not create x:/testresults/fp_files_result_test, probably not enough rights
    False
    """
    # noinspection PyBroadException
    try:
        lib_helper_functions.create_path_and_check_permission(f_path=f_path)
        return True
    except Exception:
        return False

def log_files_parameter():
    logger.info('fingerprinting directory : {}'.format(fp_files_conf.fp_dir))
    logger.info('file hashing             : {}'.format(fp_files_conf.hash_files))
    logger.info('multiprocessing          : {}'.format(fp_files_conf.multiprocessing))
    log_common_parameter()

def log_files_diff_parameter():
    logger.info('fp1       : {}'.format(fp_diff_files_conf.fp1_path))
    logger.info('fp2       : {}'.format(fp_diff_files_conf.fp2_path))
    log_common_parameter()

def log_reg_parameter():
    logger.info('field_length_limit             : {}'.format(fp_reg_conf.field_length_limit))
    logger.info('reg_save_additional_parameters : {}'.format(fp_reg_conf.reg_save_additional_parameters))
    logger.info('delete_hives                   : {}'.format(fp_reg_conf.delete_hive_copies))
    log_common_parameter()

def log_common_parameter():
    logger.info('f_output                       : {}'.format(fp_conf.f_output))
    logger.info('batchmode                      : {}'.format(not fp_conf.interactive))

def exit_message():
    logger.info('Finished\n\n')
    lib_helper_functions.logger_flush_all_handlers()
    if fp_conf.interactive:
        input('enter for exit, check the logfile')


if __name__ == '__main__':
    # Hack for multiprocessing.freeze_support() to work from a
    # setuptools-generated entry point.
    multiprocessing.freeze_support()
    fp()
