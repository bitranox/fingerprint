import csv
from lib_doctest import *
from lib_helper_functions import *
import logging
import os

logger = logging.getLogger()
setup_doctest_logger()


class ProcmonDiff(object):

    def __init__(self,
                 procmon_csv: str,
                 fingerprint_result_dir: str,
                 fingerprint_file_csv: str,
                 fingerprint_reg_csv:str):

        """
        :param fingerprint_result_dir:      e.g. c:/fingerprint
        :param procmon_csv:      e.g. procmon-logfile.CSV (in c:/fingerprint )
        :param fingerprint_reg_csv:    e.g. test-registry.csv (in c:/fingerprint )
        :param fingerprint_file_csv:  e.g. test-c-files.csv (in c:/fingerprint )
        """

        self.fingerprint_result_dir = fingerprint_result_dir
        self.procmon_csv = procmon_csv.lower().rsplit('.csv', 1)[0] + '.csv'
        self.fingerprint_reg_csv = fingerprint_reg_csv.rsplit('.csv', 1)[0] + '.csv'
        self.fingerprint_file_csv = fingerprint_file_csv.rsplit('.csv', 1)[0] + '.csv'

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def create_procmon_diff(self):
        """
        >>> procmon_diff = ProcmonDiff(fingerprint_result_dir='c:/fingerprint', procmon_csv='procmon-logfile.CSV', fingerprint_reg_name='test_registry.csv', fingerprint_files_name='test_c_files.csv')
        >>> procmon_diff.create_procmon_diff()
        """
        hashed_dict_reg = self.get_hashed_dict_fingerprint(fingerprint_csv=self.fingerprint_reg_csv)
        hashed_dict_files = self.get_hashed_dict_fingerprint(fingerprint_csv=self.fingerprint_file_csv)
        self.create_filtered_procmon_csv(hashed_dict_files=hashed_dict_files, hashed_dict_reg=hashed_dict_reg)
        self.create_filtered_fingerprints(hashed_dict_files=hashed_dict_files, hashed_dict_reg=hashed_dict_reg)

    def get_hashed_dict_fingerprint(self, fingerprint_csv:str)->{}:
        """
        :return:

        >>> procmon_diff = ProcmonDiff(fingerprint_result_dir='c:/fingerprint', procmon_csv='procmon-logfile.CSV', fingerprint_reg_name='test_registry.csv', fingerprint_files_name='test_c_files.csv')
        >>> hashed_dict = procmon_diff.get_hashed_dict_fingerprint(fingerprint_csv='test_registry.csv')
        >>> hashed_dict['HKLM\\SAM\\SAM\\Domains\\Account\\Aliases\\Members\\(default)']  # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        OrderedDict([('path', ...)])
        >>> hashed_dict = procmon_diff.get_hashed_dict_fingerprint(fingerprint_csv='test_c_files.csv')
        >>> hashed_dict['c:\\AMD']  # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        OrderedDict([('path', ...)])

        """
        hashed_dict = dict()
        fingerprint_reg_fullpath:str = os.path.join(self.fingerprint_result_dir, fingerprint_csv)
        with open(fingerprint_reg_fullpath, newline='', encoding='utf-8-sig') as csvfile:
            csv_reader = csv.DictReader(csvfile, dialect='excel')
            for dict_data in csv_reader:
                if 'value_name' in dict_data:
                    if dict_data['value_name']:  # avoid trailing '\\'
                        dict_key:str = '\\'.join([dict_data['path'], dict_data['value_name']])
                    else:
                        dict_key: str = dict_data['path']
                else:
                    dict_key: str = dict_data['path']
                hashed_dict[dict_key] = dict_data.copy()
        return hashed_dict

    def get_set_paths_procmon_accessed(self)->set:
        set_paths_procmon_accessed:set = set()
        procmon_output_fullpath: str = self.get_procmon_output_fullpath()
        with open(procmon_output_fullpath, newline='', encoding='utf-8-sig',) as procmon_accessed_file:
            csv_procmon_accessed_reader = csv.DictReader(procmon_accessed_file, dialect='excel')
            for dict_csv_procmon_accessed in csv_procmon_accessed_reader:
                set_paths_procmon_accessed.add(dict_csv_procmon_accessed['Path'])
        return set_paths_procmon_accessed

    def create_filtered_procmon_csv(self, hashed_dict_reg:{}, hashed_dict_files:{}):
        """
        >>> procmon_diff = ProcmonDiff(fingerprint_result_dir='c:/fingerprint', procmon_csv='procmon-logfile.CSV', fingerprint_reg_name='test_registry.csv', fingerprint_files_name='test_c_files.csv')
        >>> hashed_dict_reg = procmon_diff.get_hashed_dict_fingerprint(fingerprint_csv=self.fingerprint_reg_csv)
        >>> hashed_dict_files = procmon_diff.get_hashed_dict_fingerprint(fingerprint_csv=self.fingerprint_file_csv)
        >>> procmon_diff.create_filtered_procmon_csv(hashed_dict_reg=hashed_dict_reg, hashed_dict_files=hashed_dict_files)

        """
        procmon_output_fullpath:str = self.get_procmon_output_fullpath()
        procmon_input_fullpath: str = os.path.join(self.fingerprint_result_dir, self.procmon_csv)
        # open procmon output file
        with open(procmon_output_fullpath, newline='', encoding='utf-8', mode='w') as procmon_output_file:
            ls_fields:[str] = ['Time of Day', 'Process Name', 'PID', 'Operation', 'Path', 'Result', 'Detail']
            csv_procmon_output_writer = csv.DictWriter(procmon_output_file, dialect='excel', fieldnames=ls_fields)
            csv_procmon_output_writer.writeheader()
            # open procmon input file
            with open(procmon_input_fullpath, newline='', encoding='utf-8-sig') as procmon_input_file:
                csv_procmon_input_reader = csv.DictReader(procmon_input_file, dialect='excel')
                for dict_csv_procmon_input in csv_procmon_input_reader:
                    if (dict_csv_procmon_input['Path'] in hashed_dict_reg) or\
                            (dict_csv_procmon_input['Path'] in hashed_dict_files):
                        csv_procmon_output_writer.writerow(dict_csv_procmon_input)

    def create_filtered_fingerprints(self, hashed_dict_reg:{}, hashed_dict_files:{}):
        set_paths_procmon_accessed = self.get_set_paths_procmon_accessed()
        fingerprint_files_filtered_fullpath:str = self.get_fingerprint_files_filtered_fullpath()
        fingerprint_reg_filtered_fullpath:str = self.get_fingerprint_reg_filtered_fullpath()

        with open(fingerprint_files_filtered_fullpath, newline='', encoding='utf-8', mode='w') as fingerprint_files_filtered_output_file:
            ls_fields = ['path', 'size', 'created', 'modified', 'accessed', 'status', 'hash', 'change']
            fingerprint_files_filtered_output_writer = csv.DictWriter(fingerprint_files_filtered_output_file, dialect='excel', fieldnames=ls_fields)
            fingerprint_files_filtered_output_writer.writeheader()

            with open(fingerprint_reg_filtered_fullpath, newline='', encoding='utf-8', mode='w') as fingerprint_reg_filtered_output_file:
                ls_fields = ['path', 'modified', 'value_name', 'value_type', 'value', 'change', 'value_old']
                fingerprint_reg_filtered_output_writer = csv.DictWriter(fingerprint_reg_filtered_output_file, dialect='excel', fieldnames=ls_fields)
                fingerprint_reg_filtered_output_writer.writeheader()

                for path in set_paths_procmon_accessed:
                    if path in hashed_dict_reg:
                        fingerprint_reg_filtered_output_writer.writerow(hashed_dict_reg[path])
                    if path in hashed_dict_files:
                        fingerprint_files_filtered_output_writer.writerow(hashed_dict_files[path])

    def get_fingerprint_files_filtered_fullpath(self)->str:
        """
        >>> procmon_diff = ProcmonDiff(fingerprint_result_dir='c:/fingerprint', procmon_csv='procmon-logfile.CSV', fingerprint_reg_name='test-registry.csv', fingerprint_files_name = 'test_c_files.csv')
        >>> procmon_diff.get_fingerprint_files_filtered_fullpath()
        'c:/fingerprint/test_c_files_accessed_by_PROCMON_procmon-logfile.csv'
        """
        fingerprint_file_filename_basename:str = self.fingerprint_file_csv.rsplit('.', 1)[0]
        procmon_input_filename_basename:str = self.procmon_csv.rsplit('.', 1)[0]
        fingerprint_files_filtered_fullpath = fingerprint_file_filename_basename + '_accessed_by_PROCMON_{}.csv'.format(procmon_input_filename_basename)
        fingerprint_files_filtered_fullpath = convert_path_to_posix(os.path.join(self.fingerprint_result_dir, fingerprint_files_filtered_fullpath))
        return fingerprint_files_filtered_fullpath

    def get_fingerprint_reg_filtered_fullpath(self)->str:
        """
        >>> procmon_diff = ProcmonDiff(fingerprint_result_dir='c:/fingerprint', procmon_csv='procmon-logfile.CSV', fingerprint_reg_name='test-registry.csv', fingerprint_files_name = 'test_c_files.csv')
        >>> procmon_diff.get_fingerprint_reg_filtered_fullpath()
        'c:/fingerprint/test-registry_accessed_by_PROCMON_procmon-logfile.csv'
        """
        fingerprint_reg_filename_basename:str = self.fingerprint_reg_csv.rsplit('.', 1)[0]
        procmon_input_filename_basename:str = self.procmon_csv.rsplit('.', 1)[0]
        fingerprint_reg_filtered_fullpath = fingerprint_reg_filename_basename + '_accessed_by_PROCMON_{}.csv'.format(procmon_input_filename_basename)
        fingerprint_reg_filtered_fullpath = convert_path_to_posix(os.path.join(self.fingerprint_result_dir, fingerprint_reg_filtered_fullpath))
        return fingerprint_reg_filtered_fullpath

    def get_procmon_output_fullpath(self)->str:
        """
        >>> procmon_diff = ProcmonDiff(fingerprint_result_dir='c:/fingerprint', procmon_csv='procmon-logfile.CSV', fingerprint_reg_name='test-registry.csv', fingerprint_files_name = 'test_c_files.csv')
        >>> procmon_diff.get_procmon_output_fullpath()
        'c:/fingerprint/procmon-logfile_filtered_by_fingerprints_REG_test-registry_FILE_test_c_files.csv'
        """
        fingerprint_reg_filename_basename:str = self.fingerprint_reg_csv.rsplit('.', 1)[0]
        fingerprint_file_filename_basename:str = self.fingerprint_file_csv.rsplit('.', 1)[0]
        procmon_output_filename:str = self.procmon_csv.rsplit('.', 1)[0] + '_filtered_by_fingerprints_REG_{}_FILE_{}.csv'.format(fingerprint_reg_filename_basename, fingerprint_file_filename_basename)
        procmon_reg_output_fullpath = convert_path_to_posix(os.path.join(self.fingerprint_result_dir, procmon_output_filename))
        return procmon_reg_output_fullpath
