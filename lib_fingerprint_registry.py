import csv
from lib_data_structures import *
from lib_registry import get_ls_user_sids, get_username_from_sid
import lib_runcommand
import logging
from Registry import Registry

logger = logging.getLogger()

class FingerPrintRegistry(object):
    def __init__(self, fingerprint_name:str,
                 fingerprint_result_dir:str,
                 reg_save_parameters:str='',
                 field_length_limit:int=32767):
        """
        :param fingerprint_name:            the name of the fingerprint, e.g. 'test'
        :param fingerprint_result_dir:      the result dir, e.g. 'c:/test'
        :param reg_save_parameters:         additional reg save parameters, e.g. '/reg:64'
        :param field_length_limit:          data from registry, default set to maximum length of a cell in excel (32767) - we can support much longer fields
        """
        self.field_length_limit = field_length_limit  # this is the maximum length of a cell in excel
        self.fingerprint_name = fingerprint_name
        self.fingerprint_result_dir = fingerprint_result_dir
        self.reg_save_parameters = reg_save_parameters
        if not os.path.isdir(self.fingerprint_result_dir):
            os.makedirs(self.fingerprint_result_dir, exist_ok=True)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def create_fingerprint_registry(self):
        """
        >>> fingerprint_registry = FingerPrintRegistry(fingerprint_name='test', fingerprint_result_dir='c:/test')
        >>> fingerprint_registry.create_fingerprint_registry()
        """

        longest_key:str = ''
        longest_value_name:str = ''
        maximum_field_length:int = 0
        n_keys:int = 0

        logger.info('create registry fingerprint')

        logger.info('copy registry hives')
        l_registry_file_infos:[DataStructRegistryFileInfo] = self.copy_registry_files()

        logger.info('parsing hives')
        l_registry_entries = list()
        for registry_file_info in l_registry_file_infos:
            self.get_registry_file_entries(registry_file_info=registry_file_info,
                                           l_registry_entries=l_registry_entries)

        logger.info('delete registry hive copies')
        for registry_file_info in l_registry_file_infos:
            os.remove(registry_file_info.filename)

        registry_fingerprint_name = self.get_registry_fingerprint_result_filename()
        logger.info('writing registry fingerprint to {}')
        with open(registry_fingerprint_name, 'w', encoding='utf-8',newline='') as f_out:
            fieldnames = ['path', 'modified', 'value_name', 'value_type', 'value', 'change', 'value_old']
            csv_writer = csv.DictWriter(f_out, fieldnames=fieldnames, dialect='excel')
            csv_writer.writeheader()

            for registry_entry in l_registry_entries:
                n_keys += 1
                # write the key
                data_dict = dict()
                data_dict['path'] = registry_entry.path
                data_dict['modified'] = registry_entry.modified
                data_dict['value_name'] = ''
                data_dict['value_type'] = 'KEY'
                data_dict['value'] = ''
                data_dict['change'] = ''
                data_dict['value_old'] = ''
                csv_writer.writerow(data_dict)
                # write the values if any
                for registry_value in registry_entry.l_registry_values:
                    data_dict['value_name'] = registry_value.name
                    data_dict['value_type'] = registry_value.type
                    data_dict['value'] = str(registry_value.value)
                    field_length = len(data_dict['value'])
                    if field_length > maximum_field_length:
                        maximum_field_length = field_length
                        longest_key = data_dict['path']
                        longest_value_name = data_dict['value_name']

                    if field_length > self.field_length_limit:
                        logger.warning('truncating data for: {path}, value name: {value_name}, length = {field_length} to maximum length {field_length_limit}'
                                       .format(path=data_dict['path'], value_name=data_dict['value_name'], field_length=field_length, field_length_limit=self.field_length_limit))
                        data_dict['value'] = data_dict['value'][0:self.field_length_limit]
                    else:
                        csv_writer.writerow(data_dict)
            logger.info('{} registry entries written, longest value: key: {}, value_name: {}, length: {}'.format(n_keys, longest_key, longest_value_name, maximum_field_length))

    def get_registry_file_entries(self, registry_file_info:DataStructRegistryFileInfo,
                                  l_registry_entries:[DataStructRegistryEntry]):
        """
        >>> fingerprint_registry = FingerPrintRegistry(fingerprint_name='test', fingerprint_result_dir='c:/test')
        >>> registry_file_info = fingerprint_registry.copy_registry_file(registry_hive_name = 'HKLM\\SAM')
        >>> l_registry_entries = list()
        >>> fingerprint_registry.get_registry_file_entries(registry_file_info=registry_file_info, l_registry_entries=l_registry_entries)

        """
        reg = Registry.Registry(registry_file_info.filename)
        key_root = reg.root()

        logger.info('parsing registry {}'.format(registry_file_info.hive_name))
        self.get_registry_entry(key=key_root,
                                l_registry_entries=l_registry_entries,
                                registry_file_info=registry_file_info)

    def get_registry_entry(self, key:Registry.RegistryKey,
                           l_registry_entries:[DataStructRegistryEntry],
                           registry_file_info:DataStructRegistryFileInfo):

        registry_entry = DataStructRegistryEntry()
        registry_entry.path = registry_file_info.hive_name + key.path()[4:]        # cut away ROOT and add hive_name
        registry_entry.modified = key.timestamp()

        l_registry_values = list()
        for value in key.values():
            registry_value = DataStructRegistryValue()
            registry_value.name = value.name()
            registry_value.type = value.value_type_str()
            try:
                registry_value.value = value.value()
            except (AttributeError, Registry.RegistryParse.UnknownTypeException, TypeError, UnicodeDecodeError):
                s_error = 'can not read the value of key "{}", value name "{}", value type "{}"'.format(registry_entry.path, registry_value.name, registry_value.type)
                log_exception_traceback(s_error=s_error)
                registry_value.value = 'ERROR: can not be parsed or access denied'
            l_registry_values.append(registry_value)

        registry_entry.l_registry_values = l_registry_values
        l_registry_entries.append(registry_entry)

        for subkey in key.subkeys():
            self.get_registry_entry(key=subkey,
                                    l_registry_entries=l_registry_entries,
                                    registry_file_info=registry_file_info)
        return l_registry_entries

    def copy_registry_files(self)->[DataStructRegistryFileInfo]:
        l_registry_file_infos = list()
        l_hives = [('HKLM\\SAM', 'HKEY_LOCAL_MACHINE\\SAM'),
                   ('HKLM\\SECURITY', 'HKEY_LOCAL_MACHINE\\SECURITY'),
                   ('HKLM\\SOFTWARE', 'HKEY_LOCAL_MACHINE\\SOFTWARE'),
                   ('HKLM\\SYSTEM', 'HKEY_LOCAL_MACHINE\\SYSTEM'),
                   ('HKCR', 'HKEY_CLASSES_ROOT'),
                   ('HKCU', 'HKEY_CURRENT_USER')
                   ]

        l_user_hives = self.get_l_user_hives()
        l_hives = l_hives + l_user_hives

        for registry_hive_name, comment in l_hives:
            logger.info('save registry hive {}'.format(registry_hive_name))
            registry_file_info = self.copy_registry_file(registry_hive_name=registry_hive_name, comment=comment)
            if registry_file_info:
                l_registry_file_infos.append(registry_file_info)

        return l_registry_file_infos

    @staticmethod
    def get_l_user_hives()->[()]:
        """
        >>> fingerprint_registry = FingerPrintRegistry(fingerprint_name='test', fingerprint_result_dir='c:/test')
        >>> fingerprint_registry.get_l_user_hives() # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
        [('HKU\\\\.DEFAULT', 'HKEY_USERS\\\\.DEFAULT'), ...]

        """
        ls_user_sids = get_ls_user_sids()
        l_hives = []
        for user_sid in ls_user_sids:
            hive = 'HKU\\{}'.format(user_sid)
            comment = 'HKEY_USERS\\{}'.format(user_sid)
            username = get_username_from_sid(sid=user_sid)
            if username:
                comment = comment + ' ({})'.format(username)
            l_hives.append((hive, comment))
        return l_hives

    def copy_registry_file(self, registry_hive_name:str, comment:str= '')->DataStructRegistryFileInfo:
        """
        :param registry_hive_name:
        :param comment:
        :return:

        >>> fingerprint_registry = FingerPrintRegistry(fingerprint_name='test', fingerprint_result_dir='c:/test')
        >>> fingerprint_registry.copy_registry_file(registry_hive_name = 'HKLM\\SAM')

        """
        registry_hive_copy_filename = ''
        registry_file_info = DataStructRegistryFileInfo()
        # noinspection PyBroadException
        try:
            registry_hive_copy_filename = self.get_registry_hive_copy_filename(registry_hive_name)
            lib_runcommand.run_command('reg save {} '.format(registry_hive_name) + registry_hive_copy_filename + ' /y ' + self.reg_save_parameters)
            registry_file_info.filename = registry_hive_copy_filename
            registry_file_info.hive_name = registry_hive_name
            registry_file_info.comment = comment
            return registry_file_info
        except Exception:
            logger.error('can not write {registry_hive_copy_filename}, needs to run as Administrator'.format(
                registry_hive_copy_filename=registry_hive_copy_filename))

    def get_registry_hive_copy_filename(self, registry_hive_name):
        """
        :param registry_hive_name:
        :return:

        >>> fingerprint_registry = FingerPrintRegistry(fingerprint_name='test', fingerprint_result_dir='c:/test')
        >>> fingerprint_registry.get_registry_hive_copy_filename(registry_hive_name='HKLM')
        'c:/test/test_registry_hklm.hive'
        >>> fingerprint_registry.get_registry_hive_copy_filename(registry_hive_name='HKLM\\SYSTEM')
        'c:/test/test_registry_hklm_system.hive'
        """
        hive_name_filename = registry_hive_name.replace('\\', '_').lower()
        registry_filename = self.fingerprint_result_dir + '/{}_registry_{}.hive'.format(self.fingerprint_name,
                                                                                   hive_name_filename)
        return registry_filename

    def get_registry_fingerprint_result_filename(self)->str:
        """
        >>> fingerprint=FingerPrintRegistry(fingerprint_name='test', fingerprint_result_dir='c:/test')
        >>> fingerprint.get_registry_fingerprint_result_filename()
        'c:/test/test_registry.csv'
        """
        registry_fingerprint_name = convert_path_to_posix(
            os.path.join(self.fingerprint_result_dir, (self.fingerprint_name + '_registry.csv')))
        return registry_fingerprint_name
