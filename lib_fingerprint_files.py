import csv
from fp_files_conf import fp_files_conf as conf
import glob
import logging
from lib_data_structures import *
from lib_helper_functions import *
from lib_hash import get_file_hash_preserve_access_dates
import os
import concurrent.futures
from pathlib import Path

logger = logging.getLogger()

class FingerPrintFiles(object):
    def __init__(self):
        format_fp_files_dir()
        create_check_fp_result_dir()

    def __enter__(self):
        """
        >>> conf.fp_files_dir='./testfiles/'
        >>> conf.fp_result_filename='./testresults/fp_files_result1.csv'
        >>> with FingerPrintFiles() as fingerprint:
        ...   pass

        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    @staticmethod
    def create_fp():
        """
        >>> import test
        >>> timestamp = time.time()
        >>> test.create_testfiles_fingerprint_1(timestamp)
        >>> conf.fp_files_dir='./testfiles/'
        >>> conf.fp_result_filename='./testresults/fp_files_result1.csv'
        >>> fingerprint=FingerPrintFiles()
        >>> fingerprint.create_fp()

        >>> test.modify_testfiles_fingerprint_2(timestamp)
        >>> conf.fp_files_dir='./testfiles/'
        >>> conf.fp_result_filename='./testresults/fp_files_result2.csv'
        >>> fingerprint=FingerPrintFiles()
        >>> fingerprint.create_fp()

        """

        logger.info('create fingerprint for files from {}, storing results in {}'.format(conf.fp_files_dir, conf.fp_result_filename))

        n_files:int = 0
        file_iterator = get_file_iterator()

        with open(conf.fp_result_filename, 'w', encoding='utf-8', newline='') as f_out:

            fieldnames = DataStructFileInfo().get_data_dict_fieldnames()
            csv_writer = csv.DictWriter(f_out, fieldnames=fieldnames, dialect='excel')
            csv_writer.writeheader()

            for file in file_iterator:
                fileinfo = get_fileinfo(filename=file,hash_files=conf.hash_files)
                if fileinfo is not None:
                    n_files += 1
                    csv_writer.writerow(fileinfo.get_data_dict())
        logger.info('{} files fingerprinted'.format(n_files))

    @staticmethod
    def create_fp_mp():
        """
        >>> import test
        >>> timestamp = time.time()
        >>> test.create_testfiles_fingerprint_1(timestamp)
        >>> conf.fp_files_dir='./testfiles/'
        >>> conf.fp_result_filename='./testresults/fp_files_result1.csv'
        >>> fingerprint=FingerPrintFiles()
        >>> fingerprint.create_fp_mp()

        >>> test.modify_testfiles_fingerprint_2(timestamp)
        >>> conf.fp_files_dir='./testfiles/'
        >>> conf.fp_result_filename='./testresults/fp_files_result2.csv'
        >>> fingerprint=FingerPrintFiles()
        >>> fingerprint.create_fp_mp()

        """

        logger.info('create fingerprint for files from {}, storing results in {}'.format(conf.fp_files_dir, conf.fp_result_filename))

        n_files:int = 0
        file_iterator = get_file_iterator()

        with open(conf.fp_result_filename, 'w', encoding='utf-8', newline='') as f_out:
            fieldnames = DataStructFileInfo().get_data_dict_fieldnames()
            csv_writer = csv.DictWriter(f_out, fieldnames=fieldnames, dialect='excel')
            csv_writer.writeheader()

            with concurrent.futures.ProcessPoolExecutor(max_workers=int(os.cpu_count()-1)) as executor:
                fileinfo_futures = [executor.submit(get_fileinfo,filename=filename,hash_files=conf.hash_files) for filename in file_iterator]
                for fileinfo_future in concurrent.futures.as_completed(fileinfo_futures):
                    fileinfo = fileinfo_future.result()
                    if fileinfo is not None:
                        n_files += 1
                        csv_writer.writerow(fileinfo.get_data_dict())
        logger.info('{} files fingerprinted'.format(n_files))

def get_fileinfo(filename:str, hash_files:bool=True):   # we need to pass hash_files because state of conf.hash_files gets lost in MP
    """
    >>> import test
    >>> timestamp = time.time()
    >>> test.create_testfiles_fingerprint_1(timestamp)
    >>> conf.fp_files_dir='./testfiles/'
    >>> conf.fp_result_filename='./testresults/fp_files_test_result.csv'
    >>> fingerprint=FingerPrintFiles()
    >>> fileinfo = get_fileinfo('./testfiles/file1_no_changes.txt') # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    >>> fileinfo.path
    './testfiles/file1_no_changes.txt'
    >>> fileinfo.hash
    'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
    >>> fileinfo.remark
    ''
    >>> fileinfo = get_fileinfo('./testfiles/does-not-exist.txt') # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    >>> fileinfo is None
    True

    >>> fileinfo = get_fileinfo('c:/pagefile.sys')
    >>> fileinfo.remark
    'access denied'
    """

    dict_attribute_functions = {'accessed_float':os.path.getatime, 'modified_float':os.path.getmtime,
                                'created_float':os.path.getctime,'size':os.path.getsize, 'hash':get_file_hash_preserve_access_dates}

    fileinfo = DataStructFileInfo()
    fileinfo.path = filename

    for attribute,file_property_function in dict_attribute_functions.items():
        try:
            if attribute != 'hash':
                setattr(fileinfo,attribute, file_property_function(filename))
            elif hash_files:
                setattr(fileinfo, attribute, file_property_function(filename))
        except FileNotFoundError:
            fileinfo = None
            break
        except OSError:
            fileinfo.remark = 'access denied'
    return fileinfo

def get_file_iterator():
    glob_filter = conf.fp_files_dir + '**'
    file_iter = glob.iglob(glob_filter, recursive=True)
    return file_iter

def create_check_fp_result_dir():
    fp_result_dir = os.path.dirname(conf.fp_result_filename)
    try:
        if not os.path.isdir(fp_result_dir):
            os.makedirs(fp_result_dir, exist_ok=True)
        Path(conf.fp_result_filename).touch()
        os.remove(conf.fp_result_filename)
    except Exception:
        raise RuntimeError('can not create {}, probably not enough rights'.format(fp_result_dir))

def format_fp_files_dir()->str:
    """
    >>> conf.fp_files_dir='c:/'
    >>> format_fp_files_dir()
    'C:\\\\'
    >>> conf.fp_files_dir='c:/test/'
    >>> format_fp_files_dir()
    'C:\\\\test\\\\'
    >>> conf.fp_files_dir='c'
    >>> format_fp_files_dir()  # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
        ...
    RuntimeError: can not find the directory to fingerprint: c\\

    >>> conf.fp_files_dir='does_not_exist/'
    >>> format_fp_files_dir()  # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
        ...
    RuntimeError: can not find the directory to fingerprint: does_not_exist\\

    >>> conf.fp_files_dir='./testfiles/'
    >>> format_fp_files_dir()
    '.\\\\testfiles\\\\'

    >>> conf.fp_files_dir=''
    >>> format_fp_files_dir() # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
    ...
    RuntimeError: no directory to fingerprint

    >>> conf.fp_files_dir='./not_exist/'
    >>> format_fp_files_dir() # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
    ...
    RuntimeError: can not find the directory to fingerprint: .\\not_exist\\


    """
    if not conf.fp_files_dir:
        raise RuntimeError('no directory to fingerprint')

    fp_files_dir:str = conf.fp_files_dir.replace('/', '\\')
    if ':' in fp_files_dir:
        l_fp_drive_path = fp_files_dir.split(':')
        fp_files_dir = l_fp_drive_path[0].upper() + ':' + l_fp_drive_path[1]   # upper to match with procmon logfile
    if not fp_files_dir.endswith('\\'):
        fp_files_dir = fp_files_dir + '\\'
    if not os.path.isdir(fp_files_dir):
        raise RuntimeError('can not find the directory to fingerprint: {}'.format(fp_files_dir))
    conf.fp_files_dir = fp_files_dir
    return conf.fp_files_dir
