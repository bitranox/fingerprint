import csv
import glob
from lib_data_structures import *
from lib_helper_functions import *


class FingerPrintFiles(object):
    def __init__(self, fingerprint_name:str, fingerprint_result_dir:str, fingerprint_drive:str):
        self.fingerprint_name = fingerprint_name
        self.fingerprint_result_dir = fingerprint_result_dir
        self.fingerprint_drive = fingerprint_drive
        if not os.path.isdir(self.fingerprint_result_dir):
            os.makedirs(self.fingerprint_result_dir, exist_ok=True)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def create_fingerprint_files(self):
        """
        >>> fingerprint=FingerPrintFiles(fingerprint_name='test', fingerprint_result_dir='c:/test', fingerprint_drive='c:/' )
        >>> fingerprint.create_fingerprint_files()

        """

        logger.info('create fingerprint for files on drive {}'.format(self.fingerprint_drive))
        n_files:int = 0
        file_iterator = self.get_file_iterator()
        file_fingerprint_name = self.get_file_fingerprint_result_filename()
        with open(file_fingerprint_name, 'w', encoding='utf-8',newline='') as f_out:

            fieldnames = ['path', 'size', 'created', 'modified', 'accessed', 'status','change']
            csv_writer = csv.DictWriter(f_out, fieldnames=fieldnames, dialect='excel')
            csv_writer.writeheader()

            for file in file_iterator:
                fileinfo = self.get_fileinfo(file)
                if fileinfo:
                    n_files += 1
                    csv_writer.writerow(fileinfo.get_data_dict())
        logger.info('{} files fingerprinted'.format(n_files))

    @staticmethod
    def get_fileinfo(filename:str)->DataStructFileInfo:
        """
        >>> fingerprint=FingerPrintFiles(fingerprint_name='test', fingerprint_result_dir='c:/test', fingerprint_drive='c:/' )
        >>> fingerprint.get_fileinfo('c:/pagefile.sys') # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        <filesnapshot.DataStructFileInfo object at ...>
        >>> fileinfo = fingerprint.get_fileinfo('c:/does-not-exist.txt') # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        >>> fileinfo.path
        'c:/does-not-exist.txt'
        >>> fileinfo.status
        'vanished / not found'
        """

        dict_attribute_functions = {'set_accessed':os.path.getatime, 'set_modified':os.path.getmtime,
                                    'set_created':os.path.getctime,'size':os.path.getsize}

        fileinfo = DataStructFileInfo()
        fileinfo.path = filename

        for attribute,file_property_function in dict_attribute_functions.items():
            try:
                setattr(fileinfo,attribute, file_property_function(filename))
            except FileNotFoundError:
                fileinfo = None
            except OSError:
                fileinfo.status = 'access denied'
        return fileinfo

    def get_file_fingerprint_result_filename(self)->str:
        """
        >>> fingerprint=FingerPrintFiles(fingerprint_name='test', fingerprint_result_dir='c:/test', fingerprint_drive='c:/' )
        >>> fingerprint.get_file_fingerprint_result_filename()
        'c:/test/test_c_files.csv'
        """
        drive_short = self.fingerprint_drive.split(':')[0]
        file_snapshot_name = convert_path_to_posix(
            os.path.join(self.fingerprint_result_dir, (self.fingerprint_name + '_{}_files.csv'.format(drive_short))))
        return file_snapshot_name

    def get_file_iterator(self):
        fingerprint_drive = self.fingerprint_drive.split(':')[0].upper()
        glob_filter = fingerprint_drive + ':\\**'
        ls_files = glob.iglob(glob_filter, recursive=True)
        return ls_files
