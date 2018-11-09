import csv
from lib_data_structures import *
from lib_fingerprint_files import FingerPrintFiles

class FileDiff(object):
    def __init__(self,
                 fingerprint_name_1:str,
                 fingerprint_name_2:str,
                 fingerprint_result_dir:str,
                 fingerprint_drive:str):

        """
        :param fingerprint_name_1:          the name of the fingerprint1, e.g. 'before_install'
        :param fingerprint_name_2:          the name of the fingerprint2, e.g. 'after_install'
        :param fingerprint_result_dir:      the result dir, e.g. 'c:/test'
        :param fingerprint_drive:           Fingerprint Drive, for instance 'c:/'

        """

        self.fingerprint_name_1 = fingerprint_name_1
        self.fingerprint_name_2 = fingerprint_name_2
        self.fingerprint_result_dir = fingerprint_result_dir
        self.fingerprint_drive = fingerprint_drive
        self.fingerprint_files_1 = FingerPrintFiles(fingerprint_name=fingerprint_name_1,
                                                    fingerprint_result_dir=fingerprint_result_dir,
                                                    fp_drive_path=fingerprint_drive)
        self.fingerprint_files_2 = FingerPrintFiles(fingerprint_name=fingerprint_name_2,
                                                    fingerprint_result_dir=fingerprint_result_dir,
                                                    fp_drive_path=fingerprint_drive)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def create_diff_file(self):
        """
        :return:
        >>> file_diff = FileDiff(fingerprint_name_1='test', fingerprint_name_2='test', fingerprint_result_dir='c:/test', fp_drive_path='c:/')
        >>> file_diff.create_diff_file()


        """

        l_fileinfo = self.get_l_diff_fileinfo()
        self.write_diff_csv_file(l_fileinfo=l_fileinfo)

    def read_file_fingerprint_1(self)->{}:
        """
        :return:

        >>> file_diff = FileDiff(fingerprint_name_1='test', fingerprint_name_2='test2', fingerprint_result_dir='c:/test', fp_drive_path='c:/')
        >>> hashed_dict = file_diff.read_file_fingerprint_1()
        >>> hashed_dict['c:/'] # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        OrderedDict([('path', 'c:/'), ('size', '...'), ('created', '...'), ('modified', '...'), ('accessed', '...'), ('status', ''), ('change', '')])
        """
        fingerprint_filename_1:str = self.fingerprint_files_1.get_file_fingerprint_result_filename()
        hashed_dict = dict()
        with open(fingerprint_filename_1, newline='', encoding='utf-8-sig') as csvfile:
            csv_reader = csv.DictReader(csvfile, dialect='excel')
            for dict_data in csv_reader:
                hashed_dict[dict_data['path']] = dict_data.copy()
        return hashed_dict

    def get_l_diff_fileinfo(self)->[DataStructFileInfo]:
        hashed_dict_fingerprint_1 = self.read_file_fingerprint_1()
        fingerprint_result_filename_2 = self.fingerprint_files_2.get_file_fingerprint_result_filename()
        l_fileinfo:[DataStructFileInfo] = list()

        with open(fingerprint_result_filename_2, newline='', encoding='utf-8-sig') as csv_result_filename_2:
            csv_reader_result_2 = csv.DictReader(csv_result_filename_2, dialect='excel')
            # iterate new file fingerprints
            for dict_data_result_2 in csv_reader_result_2:
                # if new fingerprint
                if dict_data_result_2['path'] in hashed_dict_fingerprint_1:     # file was there before
                    # if size or modified timestamp has been changed
                    dict_data_result_1 = hashed_dict_fingerprint_1[dict_data_result_2['path']]

                    l_changed:[str] = list()
                    if dict_data_result_1['size'] != dict_data_result_2['size']:
                        l_changed.append('Size changed from {} to {}'.format(dict_data_result_1['size'],dict_data_result_2['size']))
                    if dict_data_result_1['created'] != dict_data_result_2['created']:
                        l_changed.append('Created changed from {} to {}'.format(dict_data_result_1['created'], dict_data_result_2['created']))
                    if dict_data_result_1['modified'] != dict_data_result_2['modified']:
                        l_changed.append('Modified changed from {} to {}'.format(dict_data_result_1['modified'], dict_data_result_2['modified']))
                    if dict_data_result_1['hash'] != dict_data_result_2['hash']:
                        l_changed.append('Hash (Content) changed')

                    if l_changed:
                        fileinfo = self.get_fileinfo_from_dict(dict_data_result_2)
                        fileinfo.change = ', '.join(l_changed)
                        l_fileinfo.append(fileinfo)

                    # delete the file from hashed_dict_fingerprint_1
                    hashed_dict_fingerprint_1.pop(dict_data_result_2['path'])
                else:                                                                           # new file
                    # add the new file to the result list
                    fileinfo = self.get_fileinfo_from_dict(dict_data_result_2)
                    fileinfo.change = 'ADDED'
                    l_fileinfo.append(fileinfo)

            # add the deleted files from fingerprint_1
            l_fileinfo = l_fileinfo + self.get_l_deleted_file_info(hashed_dict_fingerprint_1)
        return l_fileinfo

    def get_l_deleted_file_info(self,hashed_dict_fingerprint_result_filename_1)->[DataStructFileInfo]:
        l_fileinfo:[DataStructFileInfo] = list()
        # remaining Files were deleted
        for path, dict_file_info in hashed_dict_fingerprint_result_filename_1.items():
            fileinfo = self.get_fileinfo_from_dict(dict_file_info)
            fileinfo.change = 'DELETED'
            l_fileinfo.append(fileinfo)
        return l_fileinfo

    @staticmethod
    def get_fileinfo_from_dict(dict_file_info)->DataStructFileInfo:
        fileinfo = DataStructFileInfo()
        for key, data in dict_file_info.items():
            setattr(fileinfo, key, data)
        return fileinfo

    def write_diff_csv_file(self, l_fileinfo:[DataStructFileInfo]):
        diff_result_filename = self.get_diff_result_filename()
        with open(diff_result_filename, 'w', encoding='utf-8',newline='') as f_out:
            fieldnames = ['path', 'size', 'created', 'modified', 'accessed', 'status','hash','change']
            csv_writer = csv.DictWriter(f_out, fieldnames=fieldnames)
            csv_writer.writeheader()
            for fileinfo in l_fileinfo:
                csv_writer.writerow(fileinfo.get_data_dict())

    def get_diff_result_filename(self)->str:
        """
        >>> file_diff=FileDiff(fingerprint_name_1='test', fingerprint_name_2='test2', fingerprint_result_dir='c:/test', fp_drive_path='c:/' )
        >>> file_diff.get_diff_result_filename()
        'c:/test/diff_test_test2_c_files.csv'
        """
        drive_short = self.fingerprint_drive.split(':')[0]
        diff_result_filename = convert_path_to_posix(
            os.path.join(self.fingerprint_result_dir, ('diff_{}_{}_{}_files.csv'.format(self.fingerprint_name_1,
                                                                                        self.fingerprint_name_2,
                                                                                        drive_short))))
        return diff_result_filename
