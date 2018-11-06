import argparse
from lib_diff_files import FileDiff
from lib_diff_registry import RegistryDiff
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
    parser = argparse.ArgumentParser(description='create diff files for two system fingerprints')
    parser.add_argument('positional_ignored', type=str, nargs='*', help='Positional Arguments are ignored')
    parser.add_argument('--name1', type=str, required=False, default='', help='Fingerprint Name1, e.g. "before-install"')
    parser.add_argument('--name2', type=str, required=False, default='', help='Fingerprint Name2, e.g. "after-install"')
    parser.add_argument('--drive', type=str, required=False, default='c:/', help='Fingerprint Drive, e.g. "c:\\"')
    parser.add_argument('--target', type=str, required=False, default='c:/fingerprint',help='Fingerprint Target Directory, e.g. "c:\\fingerprint"')
    parser.add_argument('--field_length_limit', type=int, required=False, default=32767, help='data from registry, default set to maximum length of a cell in excel (32767) - we can support much longer fields')
    parser.add_argument('--check_modified', type=bool, required=False, default=False, help='check if only the modify date of a key changed - noisy ! we check also the value')
    args = parser.parse_args()
    return args

def get_logfile_fullpath(fingerprint_result_dir:str, fingerprint_name_1:str, fingerprint_name_2:str)->str:
    """
    >>> fingerprint_result_dir = 'c:/test'
    >>> fingerprint_name_1 = 'test'
    >>> fingerprint_name_2 = 'test2'
    >>> get_logfile_fullpath(fingerprint_result_dir, fingerprint_name_1, fingerprint_name_2)
    'c:/test/test_test2_diff.log'
    """
    logfile_fullpath = convert_path_to_posix(os.path.join(fingerprint_result_dir, ('{}_{}_diff.log'.format(fingerprint_name_1, fingerprint_name_2))))
    return logfile_fullpath


def main(fingerprint_name_1:str,
         fingerprint_name_2:str,
         fingerprint_drive:str,
         fingerprint_result_dir:str,
         field_length_limit: int = 32767,
         check_modified: bool = False):
    """
    :param fingerprint_name_1:          the name of the first fingerprint, e.g. 'before-install'
    :param fingerprint_name_2:          the name of the second fingerprint, e.g. 'after-install'
    :param fingerprint_drive:           Fingerprint Drive, for instance 'c:/'
    :param fingerprint_result_dir:      the result dir, e.g. 'c:/test'
    :param field_length_limit:          data from registry, default set to maximum length of a cell in excel (32767) - we can support much longer fields
    :param check_modified:              check if only the modify date of a key changed - noisy ! we check also the value

    :return:

    >>> main(fingerprint_name_1='test', fingerprint_name_2='test2', fingerprint_drive='c:/', fingerprint_result_dir='c:/test')

    """
    config_console_logger()

    logger.info('create difference between fingerprints:\n\ndrive: {}\nresults directory: {}\nregistry field_length_limit: {}\ncheck_modified_date: {}\n\n'
                .format(fingerprint_drive, fingerprint_result_dir, field_length_limit, check_modified))

    if not fingerprint_name_1:
        fingerprint_name_1 = input('name of the fingerprint_1: ')
    if not fingerprint_name_2:
        fingerprint_name_2 = input('name of the fingerprint_2: ')

    logfile_fullpath = get_logfile_fullpath(fingerprint_result_dir, fingerprint_name_1, fingerprint_name_2)
    config_file_logger(logfile_fullpath)

    logger.info('creating diff between fingerprints {} and {}'.format(fingerprint_name_1, fingerprint_name_2))

    with FileDiff(fingerprint_name_1=fingerprint_name_1,
                  fingerprint_name_2=fingerprint_name_2,
                  fingerprint_result_dir=fingerprint_result_dir,
                  fingerprint_drive=fingerprint_drive) as file_diff:
        file_diff.create_diff_file()

    with RegistryDiff(fingerprint_name_1=fingerprint_name_1,
                      fingerprint_name_2=fingerprint_name_2,
                      fingerprint_result_dir=fingerprint_result_dir,
                      field_length_limit=field_length_limit,
                      check_modified=check_modified) as registry_diff:
        registry_diff.create_diff_file()

    logger.info('Finished\n\n')
    input('enter for exit, check the logfile')


if __name__ == '__main__':
    commandline_args = get_commandline_parameters()
    main(fingerprint_name_1=commandline_args.name1,
         fingerprint_name_2=commandline_args.name2,
         fingerprint_drive=commandline_args.drive,
         fingerprint_result_dir=commandline_args.target,
         field_length_limit=commandline_args.field_length_limit,
         check_modified=commandline_args.check_modified)
