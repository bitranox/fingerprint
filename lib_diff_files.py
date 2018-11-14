import csv
from lib_data_structures import *
from fp_files_diff_conf import fp_files_diff_conf as conf

class FileDiff(object):
    def __init__(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def create_diff_file(self):
        """
        >>> conf.fp1_path = './testfiles_source/fp_files_result1_difftest.csv'
        >>> conf.fp2_path = './testfiles_source/fp_files_result2_difftest.csv'
        >>> conf.fp_result_filename = './testresults/fp_files_diff_1_2.csv'
        >>> file_diff = FileDiff()
        >>> file_diff.create_diff_file()

        """

        l_fileinfo:[DataStructFileInfo] = self.get_l_diff_fileinfo()
        self.write_diff_csv_file(l_fileinfo=l_fileinfo)

    def get_l_diff_fileinfo(self)->[DataStructFileInfo]:

        hashed_dict_fp_1 = get_hashed_dict_fp_1()

        l_fileinfo:[DataStructFileInfo] = list()

        with open(conf.fp2_path, newline='', encoding='utf-8-sig') as csv_fp_2:
            csv_reader_fp_2 = csv.DictReader(csv_fp_2, dialect='excel')
            # iterate new file fingerprints
            for dict_data_fp_2 in csv_reader_fp_2:
                # if new fingerprint
                if dict_data_fp_2['path'] in hashed_dict_fp_1:     # file was there before
                    # if size or modified timestamp has been changed
                    fileinfo_fp_2 = self.get_fileinfo_from_dict(dict_data_fp_2)
                    fileinfo_fp_1 = self.get_fileinfo_from_dict(hashed_dict_fp_1[fileinfo_fp_2.path])
                    fileinfo_fp_diff:DataStructFileInfo = self.get_fileinfo_from_dict(dict_data_fp_2)

                    b_changed:bool = False
                    b_changed_silent:bool = True
                    remark:str = ''
                    l_remark:[str] = list()

                    if fileinfo_fp_1.size != fileinfo_fp_2.size:
                        l_remark.append('Size changed from {} to {}'.format(fileinfo_fp_1.size, fileinfo_fp_2.size))
                        b_changed = True
                    if fileinfo_fp_1.created != fileinfo_fp_2.created:
                        l_remark.append('created changed from {} to {}'.format(fileinfo_fp_1.created, fileinfo_fp_2.created))
                        b_changed = True
                        b_changed_silent = False
                    if fileinfo_fp_1.modified != fileinfo_fp_2.modified:
                        l_remark.append('modified changed from {} to {}'.format(fileinfo_fp_1.modified, fileinfo_fp_2.modified))
                        b_changed = True
                        b_changed_silent = False
                    if fileinfo_fp_1.hash != fileinfo_fp_2.hash:
                        l_remark.append('hash (data) changed')
                        b_changed = True

                    if b_changed_silent:
                        fileinfo_fp_diff.change = 'CHANGED_SILENT'
                    elif b_changed:
                        fileinfo_fp_diff.change = 'CHANGED'
                    if l_remark:
                        fileinfo_fp_diff.remark = ', '.join(l_remark)
                        l_fileinfo.append(fileinfo_fp_diff)

                    # delete the file from hashed_dict_fp_1
                    hashed_dict_fp_1.pop(dict_data_fp_2['path'])
                else:                                                                           # new file
                    # add the new file to the result list
                    fileinfo_fp_diff = self.get_fileinfo_from_dict(dict_data_fp_2)
                    fileinfo_fp_diff.change = 'ADDED'
                    l_fileinfo.append(fileinfo_fp_diff)

            # add the deleted files from fingerprint_1
            l_fileinfo = l_fileinfo + self.get_l_deleted_file_info(hashed_dict_fp_1)
        return l_fileinfo

    def get_l_deleted_file_info(self, hashed_dict_fp_1)->[DataStructFileInfo]:
        l_fileinfo:[DataStructFileInfo] = list()
        # remaining Files were deleted
        for path, dict_file_info in hashed_dict_fp_1.items():
            fileinfo_fp_diff = self.get_fileinfo_from_dict(dict_file_info)
            fileinfo_fp_diff.change = 'DELETED'
            l_fileinfo.append(fileinfo_fp_diff)
        return l_fileinfo

    @staticmethod
    def get_fileinfo_from_dict(dict_file_info)->DataStructFileInfo:
        fileinfo = DataStructFileInfo()
        for key, data in dict_file_info.items():
            setattr(fileinfo, key, data)
        return fileinfo

    def write_diff_csv_file(self, l_fileinfo:[DataStructFileInfo]):
        with open(conf.fp_result_filename, 'w', encoding='utf-8',newline='') as f_out:
            fieldnames = DataStructFileInfo().get_data_dict_fieldnames()
            csv_writer = csv.DictWriter(f_out, fieldnames=fieldnames)
            csv_writer.writeheader()
            for fileinfo in l_fileinfo:
                csv_writer.writerow(fileinfo.get_data_dict())

def get_hashed_dict_fp_1()->{}:
    """
    :return:

    >>> conf.fp1_path = './testfiles_source/fp_files_result1_difftest.csv'
    >>> hashed_dict = get_hashed_dict_fp_1()
    >>> hashed_dict  # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    {'.\\\\testfiles\\\\file1_no_changes.txt': OrderedDict([...])}
    """
    hashed_dict = dict()
    with open(conf.fp1_path, newline='', encoding='utf-8-sig') as csvfile:
        csv_reader = csv.DictReader(csvfile, dialect='excel')
        for dict_data in csv_reader:
            hashed_dict[dict_data['path']] = dict_data.copy()
    return hashed_dict
