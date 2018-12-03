import csv
from lib_data_structures import *
from lib_fp_registry import FingerPrintRegistry

class RegistryDiff(object):
    def __init__(self,
                 fingerprint_name_1:str,
                 fingerprint_name_2:str,
                 fingerprint_result_dir:str,
                 field_length_limit:int=32767,
                 check_modified:bool=False):
        """
        :param fingerprint_name_1:          the name of the fingerprint1, e.g. 'before_install'
        :param fingerprint_name_2:          the name of the fingerprint2, e.g. 'after_install'
        :param fingerprint_result_dir:      the result dir, e.g. 'c:/test'
        :param field_length_limit:          data from registry, default set to maximum length of a cell in excel (32767) - we can support much longer fields
        :param check_modified:              check if only the modify date of a key changed - noisy ! we check also the value
        """
        self.fingerprint_name_1 = fingerprint_name_1
        self.fingerprint_name_2 = fingerprint_name_2
        self.fingerprint_result_dir = fingerprint_result_dir
        self.fingerprint_registry_1 = FingerPrintRegistry(fingerprint_name=fingerprint_name_1,
                                                          fingerprint_result_dir=fingerprint_result_dir)
        self.fingerprint_registry_2 = FingerPrintRegistry(fingerprint_name=fingerprint_name_2,
                                                          fingerprint_result_dir=fingerprint_result_dir)
        self.field_length_limit: int = field_length_limit   # this is the maximum length of a cell in excel

        if self.field_length_limit > 131072:                # set the field length in csv reader accordingly
            csv.field_size_limit(min(sys.maxsize,self.field_length_limit+10000))

        self.check_modified = check_modified                # check if only the modify date of a key changed - noisy ! we check also the value

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def create_diff_file(self):
        """
        :return:
        >>> file_diff = RegistryDiff(fingerprint_name_1='test', fingerprint_name_2='test2', fingerprint_result_dir='c:/test')
        >>> file_diff.create_diff_file()
        """

        l_dict_diff_registry_info = self.get_l_dict_diff_registry_info()
        self.write_diff_csv_file(l_dict_registry_info=l_dict_diff_registry_info)

    def get_hashed_dict_fingerprint_1(self)->{}:
        """
        :return:

        >>> file_diff = RegistryDiff(fingerprint_name_1='test', fingerprint_name_2='test2', fingerprint_result_dir='c:/test')
        >>> hashed_dict = file_diff.get_hashed_dict_fingerprint_1()
        >>> hashed_dict[('HKLM\\SAM\\SAM\\Domains','(default)')]  # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        OrderedDict([('path', 'HKLM\\SAM\\SAM\\Domains'), ('modified', '...'), ('value_name', '(default)'), ('value_type', 'RegNone'), ('value', "b''"), ('change', ''), ('value_old', '')])

        """
        fingerprint_filename_1:str = self.fingerprint_registry_1.get_registry_fingerprint_result_filename()
        hashed_dict = dict()
        with open(fingerprint_filename_1, newline='', encoding='utf-8-sig') as csvfile:
            csv_reader = csv.DictReader(csvfile, dialect='excel')
            for dict_data in csv_reader:
                hashed_dict[(dict_data['path'],dict_data['value_name'])] = dict_data.copy()
        return hashed_dict

    def get_l_dict_diff_registry_info(self)->[{}]:
        hashed_dict_fingerprint_1 = self.get_hashed_dict_fingerprint_1()
        fingerprint_result_filename_2 = self.fingerprint_registry_2.get_registry_fingerprint_result_filename()
        l_dict_data_diff:[{}] = list()

        with open(fingerprint_result_filename_2, newline='', encoding='utf-8-sig') as csv_result_filename_2:
            csv_reader_result_2 = csv.DictReader(csv_result_filename_2, dialect='excel')
            # iterate new file fingerprints
            for dict_data_result_2 in csv_reader_result_2:
                # if new fingerprint
                if (dict_data_result_2['path'],dict_data_result_2['value_name']) in hashed_dict_fingerprint_1:     # registry entry was there before
                    # if something has been changed
                    dict_data_result_1 = hashed_dict_fingerprint_1[(dict_data_result_2['path'],dict_data_result_2['value_name'])]

                    l_changed:[str] = list()
                    if self.check_modified and (dict_data_result_1['modified'] != dict_data_result_2['modified']):
                        l_changed.append('modified changed from {} to {}'.format(dict_data_result_1['modified'], dict_data_result_2['modified']))
                    if dict_data_result_1['value_type'] != dict_data_result_2['value_type']:
                        l_changed.append('value_type changed from {} to {}'.format(dict_data_result_1['value_type'], dict_data_result_2['value_type']))
                    if dict_data_result_1['value'] != dict_data_result_2['value']:
                        l_changed.append('value changed')
                        dict_data_result_2['value_old'] = dict_data_result_1['value']
                    if l_changed:
                        dict_data_result_2['change'] = ' ,'.join(l_changed)
                        l_dict_data_diff.append(dict_data_result_2.copy())

                    # delete the registry item from hashed_dict_fingerprint_1
                    hashed_dict_fingerprint_1.pop((dict_data_result_2['path'],dict_data_result_2['value_name']))
                else:                                                                           # new file
                    # add the new registry item to the result list
                    dict_data_result_2['change'] = 'ADDED'
                    l_dict_data_diff.append(dict_data_result_2.copy())

            # add the deleted registry items from fingerprint_1
            l_dict_data_diff = l_dict_data_diff + self.get_l_deleted_registry_info(hashed_dict_fingerprint_1)
        return l_dict_data_diff

    @staticmethod
    def get_l_deleted_registry_info(hashed_dict_fingerprint_result_filename_1)->[{}]:
        l_dict_registry_info:[{}] = list()
        # remaining entries were deleted
        for path, dict_registry_info in hashed_dict_fingerprint_result_filename_1.items():
            dict_registry_info.change = 'DELETED'
            l_dict_registry_info.append(dict_registry_info.copy())
        return l_dict_registry_info

    @staticmethod
    def get_fileinfo_from_dict(dict_file_info)->DataStructFileInfo:
        fileinfo = DataStructFileInfo()
        for key, data in dict_file_info.items():
            setattr(fileinfo, key, data)
        return fileinfo

    def write_diff_csv_file(self, l_dict_registry_info:[dict]):
        diff_result_filename = self.get_diff_result_filename()
        with open(diff_result_filename, 'w', encoding='utf-8',newline='') as f_out:
            fieldnames = ['path', 'modified', 'value_name', 'value_type', 'value', 'change', 'value_old']
            csv_writer = csv.DictWriter(f_out, fieldnames=fieldnames)
            csv_writer.writeheader()
            for dict_registry_info in l_dict_registry_info:
                csv_writer.writerow(dict_registry_info)

    def get_diff_result_filename(self)->str:
        """
        >>> registry_diff=RegistryDiff(fingerprint_name_1='test', fingerprint_name_2='test2', fingerprint_result_dir='c:/test')
        >>> registry_diff.get_diff_result_filename()
        'c:/test/diff_test_test2_registry.csv'
        """
        diff_result_filename = convert_path_to_posix(
            os.path.join(self.fingerprint_result_dir, ('diff_{}_{}_registry.csv'.format(self.fingerprint_name_1,
                                                                                        self.fingerprint_name_2))))
        return diff_result_filename
