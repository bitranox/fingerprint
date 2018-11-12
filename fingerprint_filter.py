import argparse
from lib_filter_procmon import ProcmonDiff
from lib_helper_functions import *
import lib_doctest
import logging
import sys

logger = logging.getLogger()
lib_doctest.setup_doctest_logger()

def get_commandline_parameters():
    """
    >>> sys.argv.append('--procmon_csv=procmon-logfile')
    >>> sys.argv.append('--fingerprint_file_csv=test_c_files')
    >>> sys.argv.append('--fingerprint_reg_csv=test_registry')
    >>> sys.argv.append('--target=c:/fingerprint')
    >>> args = get_commandline_parameters()
    >>> args.target
    'c:/fingerprint'
    """
    parser = argparse.ArgumentParser(description='filter fingerprints and procmon logfile')
    parser.add_argument('positional_ignored', type=str, nargs='*', help='Positional Arguments are ignored')
    parser.add_argument('--procmon_csv', type=str, required=False, default='', help='name of the procmon Logfile, e.g. "procmon-logfile.CSV"')
    parser.add_argument('--fingerprint_file_csv', type=str, required=False, default='', help='name of the fingerprint for files, e.g. "test_c_files.csv"')
    parser.add_argument('--fingerprint_reg_csv', type=str, required=False, default='', help='name of the fingerprint for registry, e.g. "test_registry.csv"')
    parser.add_argument('--target', type=str, required=False, default='c:/fingerprint',help='Fingerprint Target Directory, e.g. "c:\\fingerprint"')
    args = parser.parse_args()
    return args

def get_logfile_fullpath(fingerprint_result_dir, procmon_csv:str, fingerprint_file_csv:str, fingerprint_reg_csv:str)->str:
    """
    >>> fingerprint_result_dir = 'c:/fingerprint'
    >>> procmon_csv = 'procmon-logfile'
    >>> fingerprint_file_csv = 'test_c_files'
    >>> fingerprint_reg_csv = 'test_registry'
    >>> set_logfile_fullpath(fingerprint_result_dir, procmon_csv, fingerprint_file_csv, fingerprint_reg_csv)
    'c:/fingerprint/PM_procmon-logfile_FPF_test_c_files_FPR_test_registry.log'

    >>> procmon_csv = 'procmon-logfile'
    >>> fingerprint_file_csv = 'test_c_files'
    >>> fingerprint_reg_csv = 'test_registry'
    >>> set_logfile_fullpath(fingerprint_result_dir, procmon_csv, fingerprint_file_csv, fingerprint_reg_csv)
    'c:/fingerprint/PM_procmon-logfile_FPF_test_c_files_FPR_test_registry.log'

    >>> procmon_csv = 'procmon-logfile.csv'
    >>> fingerprint_file_csv = 'test_c_files.csv'
    >>> fingerprint_reg_csv = 'test_registry.csv'
    >>> set_logfile_fullpath(fingerprint_result_dir, procmon_csv, fingerprint_file_csv, fingerprint_reg_csv)
    'c:/fingerprint/PM_procmon-logfile_FPF_test_c_files_FPR_test_registry.log'


    """
    procmon_csv = procmon_csv.lower().rsplit('.csv',1)[0]
    fingerprint_file_csv = fingerprint_file_csv.lower().rsplit('.csv', 1)[0]
    fingerprint_reg_csv = fingerprint_reg_csv.lower().rsplit('.csv', 1)[0]
    logfile_fullpath = convert_path_to_posix(os.path.join(fingerprint_result_dir, ('PM_{}_FPF_{}_FPR_{}.log'.format(procmon_csv, fingerprint_file_csv, fingerprint_reg_csv))))
    return logfile_fullpath


def main(procmon_csv:str,
         fingerprint_result_dir:str,
         fingerprint_file_csv:str,
         fingerprint_reg_csv:str):
    """
    :param procmon_csv:                 the name of the procmon Logfile, e.g. 'procmon-logfile'
    :param fingerprint_result_dir:      the result dir, e.g. 'c:/fingerprint'
    :param fingerprint_file_csv:        the name of the fingerprint for files, e.g. 'test_c_files'
    :param fingerprint_reg_csv:         the name of the fingerprint for registry, e.g. 'test_registry'

    :return:

    >>> main(procmon_csv='procmon-logfile', fingerprint_file_csv='test_c_files', fingerprint_reg_csv='test_registry', fingerprint_result_dir='c:/fingerprint')

    """
    config_console_logger()

    logger.info('filter procmon logfile from fingerprints')

    if not procmon_csv:
        procmon_csv = input('filename of the procmon logfile csv (e.g. procmon-test1.csv): ')
    if not fingerprint_file_csv:
        fingerprint_file_csv = input('filename of the file fingerprint (e.g. test_c_files.csv): ')
    if not fingerprint_reg_csv:
        fingerprint_reg_csv = input('filename of the registry fingerprint (e.g. test_registry.csv): ')

    logfile_fullpath = get_logfile_fullpath(fingerprint_result_dir=fingerprint_result_dir,
                                            procmon_csv=procmon_csv,
                                            fingerprint_file_csv=fingerprint_file_csv,
                                            fingerprint_reg_csv=fingerprint_reg_csv)
    config_file_logger(logfile_fullpath)

    logger.info('filtering {}, {} and {}'.format(fingerprint_file_csv, fingerprint_reg_csv, procmon_csv))

    with ProcmonDiff(procmon_csv=procmon_csv,
                     fingerprint_result_dir=fingerprint_result_dir,
                     fingerprint_file_csv=fingerprint_file_csv,
                     fingerprint_reg_csv=fingerprint_reg_csv) as procmon_diff:
        procmon_diff.create_procmon_diff()

    logger.info('Finished\n\n')
    input('enter for exit, check the logfile')


if __name__ == '__main__':
    commandline_args = get_commandline_parameters()
    main(procmon_csv=commandline_args.procmon_csv,
         fingerprint_result_dir=commandline_args.target,
         fingerprint_file_csv=commandline_args.fingerprint_file_csv,
         fingerprint_reg_csv=commandline_args.fingerprint_reg_csv)
