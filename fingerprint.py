import argparse
from lib_fingerprint_files import FingerPrintFiles
from lib_fingerprint_registry import FingerPrintRegistry
from lib_helper_functions import *
import lib_doctest
import logging
import sys

logger = logging.getLogger()
lib_doctest.setup_doctest_logger()

def get_commandline_parameters():
    """
    >>> sys.argv.append('--name=test')
    >>> sys.argv.append('--drive=c:/')
    >>> sys.argv.append('--target=c:/test')
    >>> args = get_commandline_parameters()
    >>> args.target
    'c:/test'
    >>> args.reg_save_param
    ''
    """
    parser = argparse.ArgumentParser(description='create fingerprint of the system')
    parser.add_argument('positional_ignored', type=str, nargs='*', help='Positional Arguments are ignored')
    parser.add_argument('--name', type=str, required=False, default='', help='Fingerprint Name, e.g. "before_install"')
    parser.add_argument('--drive', type=str, required=False, default='c:/', help='Fingerprint Drive, e.g. "c:\\"')
    parser.add_argument('--target', type=str, required=False, default='c:/fingerprint', help='Fingerprint Target Directory, e.g. "c:\\fingerprint"')
    parser.add_argument('--reg_save_param', type=str, required=False, default='', help='optional reg save parameters, e.g. "/reg:64" or "/reg:32"')
    parser.add_argument('--field_length_limit', type=int, required=False, default=32767, help='data from registry, default set to maximum length of a cell in excel (32767) - we can support much longer fields')
    args = parser.parse_args()
    return args

def get_logfile_fullpath(fingerprint_result_dir:str, fingerprint_name:str)->str:
    """
    :param fingerprint_result_dir:
    :param fingerprint_name:
    :return:

    >>> fingerprint_result_dir = 'c:/test'
    >>> fingerprint_name = 'test'
    >>> get_logfile_fullpath(fingerprint_result_dir, fingerprint_name)
    'c:/test/test.log'
    """
    logfile_fullpath = convert_path_to_posix(os.path.join(fingerprint_result_dir, (fingerprint_name + '.log')))
    return logfile_fullpath


def main(fingerprint_name:str,
         fingerprint_drive:str,
         fingerprint_result_dir:str,
         reg_save_parameters:str='',
         field_length_limit:int=32767):
    """
    :param fingerprint_name:            the name of the fingerprint, e.g. 'test'
    :param fingerprint_drive:           Fingerprint Drive, for instance 'c:/'
    :param fingerprint_result_dir:      the result dir, e.g. 'c:/test'
    :param reg_save_parameters:         additional reg save parameters, e.g. '/reg:64 or /reg:32'
    :param field_length_limit:          data from registry, default set to maximum length of a cell in excel (32767) - we can support much longer fields
    :return:

    >>> main(fingerprint_name='test', fingerprint_drive='c:/', fingerprint_result_dir='c:/test')

    """

    config_console_logger()
    exit_if_not_run_as_admin()
    logger.info('create fingerprint')
    logger.info('fingerprinting drive : {}'.format(fingerprint_drive))
    logger.info('results directory    : {}'.format(fingerprint_result_dir))
    logger.info('reg_save_parameters  : {}'.format(reg_save_parameters))
    logger.info('field_length_limit   : {}'.format(field_length_limit))

    if not fingerprint_name:
        fingerprint_name = input('name of the fingerprint: ')

    logger.info('fingerprint_name     : {}'.format(fingerprint_name))

    logfile_fullpath = get_logfile_fullpath(fingerprint_result_dir, fingerprint_name)
    config_file_logger(logfile_fullpath)

    with FingerPrintFiles(fingerprint_name=fingerprint_name,
                          fingerprint_result_dir=fingerprint_result_dir,
                          fingerprint_drive=fingerprint_drive) as fingerprint_files:
        fingerprint_files.create_fingerprint_files()

    with FingerPrintRegistry(fingerprint_name=fingerprint_name,
                             fingerprint_result_dir=fingerprint_result_dir,
                             reg_save_parameters=reg_save_parameters,
                             field_length_limit=field_length_limit) as fingerprint_registry:
        fingerprint_registry.create_fingerprint_registry()

    logger.info('Finished\n\n')
    logger_flush_all_handlers()
    input('enter for exit, check the logfile')


if __name__ == '__main__':
    commandline_args = get_commandline_parameters()
    main(fingerprint_name=commandline_args.name,
         fingerprint_drive=commandline_args.drive,
         fingerprint_result_dir=commandline_args.target,
         reg_save_parameters=commandline_args.reg_save_param,
         field_length_limit=commandline_args.field_length_limit)
