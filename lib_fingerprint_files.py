import csv
import glob
from lib_data_structures import *
from lib_helper_functions import *
from lib_hash import get_file_hash_preserve_access_dates
import os

class FingerPrintFiles(object):
    def __init__(self, fp_drive_path:str, fp_result_fullpath:str):
        self.fp_result_fullpath:str = fp_result_fullpath
        self.fp_drive_path = self.format_fp_drive_path(fp_drive_path)
        self.create_fp_result_dir()

    def __enter__(self):
        """
        >>> with FingerPrintFiles(fp_drive_path='./testfiles/', fp_result_fullpath='./testresults/fp_files1_result.csv') as fingerprint:
        ...   pass

        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def create_fingerprint_files(self):
        """
        >>> import test
        >>> timestamp = time.time()
        >>> test.create_testfiles_fingerprint_1(timestamp)
        >>> fingerprint=FingerPrintFiles(fp_drive_path='./testfiles/', fp_result_fullpath='./testresults/fp_files1_result.csv')
        >>> fingerprint.create_fingerprint_files()
        >>> test.modify_testfiles_fingerprint_2(timestamp)
        >>> fingerprint=FingerPrintFiles(fp_drive_path='./testfiles/', fp_result_fullpath='./testresults/fp_files2_result.csv')
        >>> fingerprint.create_fingerprint_files()

        """

        logger.info('create fingerprint for files from {}, storing results in {}'.format(self.fp_drive_path, self.fp_result_fullpath))
        n_files:int = 0
        file_iterator = self.get_file_iterator()
        with open(self.fp_result_fullpath, 'w', encoding='utf-8',newline='') as f_out:

            fieldnames = DataStructFileInfo().get_data_dict_fieldnames()
            csv_writer = csv.DictWriter(f_out, fieldnames=fieldnames, dialect='excel')
            csv_writer.writeheader()

            for file in file_iterator:
                fileinfo = self.get_fileinfo(file)
                if fileinfo:
                    n_files += 1
                    csv_writer.writerow(fileinfo.get_data_dict())
        logger.info('{} files fingerprinted'.format(n_files))

    @staticmethod
    def get_fileinfo(filename:str):
        """
        >>> import test
        >>> timestamp = time.time()
        >>> test.create_testfiles_fingerprint_1(timestamp)
        >>> fingerprint=FingerPrintFiles(fp_drive_path='./testfiles/', fp_result_fullpath='./testresults/fp_files_test_result.csv')
        >>> fileinfo = fingerprint.get_fileinfo('./testfiles/file1_no_changes.txt') # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        >>> fileinfo.path
        './testfiles/file1_no_changes.txt'
        >>> fileinfo.hash
        'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
        >>> fileinfo.remark
        ''
        >>> fileinfo = fingerprint.get_fileinfo('./testfiles/does-not-exist.txt') # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        >>> fileinfo is None
        True

        >>> fileinfo = fingerprint.get_fileinfo('c:/pagefile.sys')
        >>> fileinfo.remark
        'access denied'

        """

        dict_attribute_functions = {'accessed_float':os.path.getatime, 'modified_float':os.path.getmtime,
                                    'created_float':os.path.getctime,'size':os.path.getsize, 'hash':get_file_hash_preserve_access_dates}

        fileinfo = DataStructFileInfo()
        fileinfo.path = filename

        for attribute,file_property_function in dict_attribute_functions.items():
            try:
                setattr(fileinfo,attribute, file_property_function(filename))
            except FileNotFoundError:
                fileinfo = None
            except OSError:
                fileinfo.remark = 'access denied'
        return fileinfo

    def get_file_iterator(self):
        glob_filter = self.fp_drive_path + '**'
        file_iter = glob.iglob(glob_filter, recursive=True)
        return file_iter

    def create_fp_result_dir(self):
        """
        >>> fingerprint=FingerPrintFiles(fp_drive_path='./testfiles/', fp_result_fullpath='x:/testresults/fp_files_test_result.csv')  # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        Traceback (most recent call last):
            ...
        RuntimeError: can not create x:/testresults, probably not enough rights
        """
        fp_result_dir = os.path.dirname(self.fp_result_fullpath)
        try:
            if not os.path.isdir(fp_result_dir):
                os.makedirs(fp_result_dir, exist_ok=True)
        except Exception:
            raise RuntimeError('can not create {}, probably not enough rights'.format(fp_result_dir))

    @staticmethod
    def format_fp_drive_path(fp_drive_path:str)->str:
        """
        >>> import test
        >>> timestamp = time.time()
        >>> test.create_testfiles_fingerprint_1(timestamp)
        >>> fingerprint=FingerPrintFiles(fp_drive_path='./testfiles/', fp_result_fullpath='./testresults/fp_files_test_result.csv')
        >>> fingerprint.format_fp_drive_path(fp_drive_path='c:/')
        'C:\\\\'
        >>> fingerprint.format_fp_drive_path(fp_drive_path='c:/test/')
        'C:\\\\test\\\\'
        >>> fingerprint.format_fp_drive_path(fp_drive_path='c')  # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        Traceback (most recent call last):
            ...
        RuntimeError: the path to fingerprint has to end with "\\" or "/"

        >>> fingerprint.format_fp_drive_path(fp_drive_path='does_not_exist/')  # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        Traceback (most recent call last):
            ...
        RuntimeError: can not find the drive to fingerprint: does_not_exist\\

        """
        fp_drive_path:str = fp_drive_path.replace('/','\\')
        if ':' in fp_drive_path:
            l_fp_drive_path = fp_drive_path.split(':')
            fp_drive_path = l_fp_drive_path[0].upper() + ':' + l_fp_drive_path[1]   # upper to match with procmon logfile
        if not fp_drive_path.endswith('\\'):
            raise RuntimeError('the path to fingerprint has to end with "\\" or "/"')
        if not os.path.isdir(fp_drive_path):
            raise RuntimeError('can not find the drive to fingerprint: {}'.format(fp_drive_path))
        return fp_drive_path
