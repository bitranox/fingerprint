import csv
from fp_conf import fp_conf, fp_reg_conf
import lib_data_structures
import lib_detect_encoding
import lib_helper_functions
import lib_registry
import lib_runcommand
import logging
import os
from Registry import Registry

logger = logging.getLogger()

class FingerPrintRegistry(object):
    def __init__(self):
        pass

    def __enter__(self):
        """
        >>> with FingerPrintRegistry() as fingerprint_registry:
        ...    pass

        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def create_fingerprint_registry(self):
        """
        >>> fingerprint_registry = FingerPrintRegistry()
        >>> fingerprint_registry.create_fingerprint_registry()
        """
        logger.info('create registry fingerprint')
        registry_files_copied:[lib_data_structures.DataStructRegistryFileInfo] = self.copy_registry_files_and_return_copied()
        l_registry_entries: [lib_data_structures.DataStructRegistryEntry] = self.parse_all_hives(registry_files_copied)
        if fp_reg_conf.delete_hive_copies:
            self.delete_hive_copies(registry_files_copied)
        self.write_registry_entries_to_csv(l_registry_entries)

    @staticmethod
    def write_registry_entries_to_csv(l_registry_entries:[lib_data_structures.DataStructRegistryEntry]):
        """
        >>> fingerprint_registry = FingerPrintRegistry()
        >>> fp_conf.f_output = './testfiles/test_reg.csv'
        >>> registry_file_info = lib_data_structures.DataStructRegistryFileInfo()
        >>> registry_file_info.hive_name = 'HKLM\SAM'
        >>> registry_file_info.filename = './testfiles_source/test_registry_hklm_sam.hive'
        >>> l_registry_entries = fingerprint_registry.parse_hive(registry_file_info=registry_file_info)  # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
        >>> fingerprint_registry.write_registry_entries_to_csv(l_registry_entries=l_registry_entries)
        """

        n_keys:int = 0
        longest_key:str = ''
        longest_value_name:str = ''
        maximum_field_length:int = 0
        logger.info('writing registry fingerprint to {}'.format(fp_conf.f_output))
        with open(fp_conf.f_output, 'w', encoding='utf-8',newline='') as f_out:
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

                    if field_length > fp_reg_conf.field_length_limit:
                        logger.warning('truncating data for: {}, value name: {}, length = {} to maximum length {}'
                                       .format(data_dict['path'], data_dict['value_name'],
                                               field_length, fp_reg_conf.field_length_limit))
                        data_dict['value'] = data_dict['value'][0:fp_reg_conf.field_length_limit]
                    else:
                        csv_writer.writerow(data_dict)
            logger.info('{} registry entries written, longest value: key: {}, value_name: {}, length: {}'.format(n_keys, longest_key, longest_value_name, maximum_field_length))

    def parse_all_hives(self, registry_files_copied:[lib_data_structures.DataStructRegistryFileInfo])->[lib_data_structures.DataStructRegistryEntry]:
        logger.info('parsing hives')
        l_all_reg_entries = list()
        for registry_file_info in registry_files_copied:
            l_reg_entries = self.parse_hive(registry_file_info=registry_file_info)
            l_all_reg_entries = l_all_reg_entries + l_reg_entries
        return l_all_reg_entries

    def parse_hive(self, registry_file_info:lib_data_structures.DataStructRegistryFileInfo)->[lib_data_structures.DataStructRegistryEntry]:
        """
        >>> fingerprint_registry = FingerPrintRegistry()
        >>> registry_file_info = lib_data_structures.DataStructRegistryFileInfo()
        >>> registry_file_info.hive_name = 'HKLM\SAM'
        >>> registry_file_info.filename = './testfiles_source/test_registry_hklm_sam.hive'
        >>> fingerprint_registry.parse_hive(registry_file_info=registry_file_info)  # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
        [<lib_data_structures.DataStructRegistryEntry object at ...>, ...]
        """
        reg = Registry.Registry(registry_file_info.filename)
        key_root = reg.root()
        logger.info('registry key root : {}'.format(key_root))
        logger.info('parsing registry {}'.format(registry_file_info.hive_name))
        l_reg_entries = self.get_registry_entries(key=key_root, registry_file_info=registry_file_info)
        return l_reg_entries

    def get_registry_entries(self, key:Registry.RegistryKey, registry_file_info:lib_data_structures.DataStructRegistryFileInfo)->[lib_data_structures.DataStructRegistryEntry]:
        l_reg_entries = list()
        l_registry_values = list()
        registry_entry = lib_data_structures.DataStructRegistryEntry()
        registry_entry.path = self.format_key_path(registry_file_info=registry_file_info, key_path=key.path())
        registry_entry.modified = key.timestamp()

        for value in key.values():
            registry_value = lib_data_structures.DataStructRegistryValue()
            registry_value.name = value.name()
            registry_value.type = value.value_type_str()
            try:
                registry_value.value = self.get_registry_value(value)
            except (AttributeError, Registry.RegistryParse.UnknownTypeException, TypeError, UnicodeDecodeError):
                s_error = 'can not read the value of key "{}", value name "{}", value type "{}"'.format(registry_entry.path, registry_value.name, registry_value.type)
                lib_helper_functions.log_exception_traceback(s_error=s_error)
                registry_value.value = 'ERROR: can not be parsed or access denied'
            l_registry_values.append(registry_value)

        registry_entry.l_registry_values = l_registry_values
        l_reg_entries.append(registry_entry)

        for subkey in key.subkeys():
            l_subkeys = self.get_registry_entries(key=subkey, registry_file_info=registry_file_info)
            l_reg_entries = l_reg_entries + l_subkeys
        return l_reg_entries

    @staticmethod
    def get_registry_value(value)->str:
        try:
            registry_value = value.value()
        except (AttributeError, Registry.RegistryParse.UnknownTypeException, TypeError, UnicodeDecodeError):
            value_raw = value.raw_data()
            encoding = lib_detect_encoding.detect_encoding(value_raw)
            registry_value = value_raw.decode(encoding)
        return registry_value

    @staticmethod
    def format_key_path(registry_file_info:lib_data_structures.DataStructRegistryFileInfo, key_path:str)->str:
        """
        >>> fingerprint_registry = FingerPrintRegistry()
        >>> registry_file_info = lib_data_structures.DataStructRegistryFileInfo()
        >>> registry_file_info.hive_name = 'HKLM\\SOFTWARE'
        >>> key_path = 'ROOT\\\\'
        >>> fingerprint_registry.format_key_path(registry_file_info=registry_file_info, key_path=key_path)
        'HKLM\\\\SOFTWARE\\\\'
        >>> key_path = 'CMI-CreateHive\\\\'
        >>> fingerprint_registry.format_key_path(registry_file_info=registry_file_info, key_path=key_path)
        'HKLM\\\\SOFTWARE\\\\'
        >>> key_path = 'Microsoft\\\\Test'
        >>> fingerprint_registry.format_key_path(registry_file_info=registry_file_info, key_path=key_path)
        'HKLM\\\\SOFTWARE\\\\Microsoft\\\\Test'

        """
        # python-registry unclear: on some hives the path starts with ROOT\, on some not - so just fix it here
        # sometimes the path starts with CMI-CreateHive{......}\ - just fix it here
        if key_path.startswith('ROOT\\') or key_path.startswith('CMI-CreateHive'):
            l_key_path = key_path.split('\\',1)
            if len(l_key_path) > 1:                     # if key == 'ROOT\\'
                key_path = key_path.split('\\',1)[1]
            else:
                key_path = ''
        key_path = registry_file_info.hive_name + '\\' + key_path
        return key_path

    def copy_registry_files_and_return_copied(self)->[lib_data_structures.DataStructRegistryFileInfo]:
        """
        >>> fingerprint_registry = FingerPrintRegistry()
        >>> fp_conf.f_output = 'c:/test/test.csv'
        >>> fingerprint_registry.copy_registry_files_and_return_copied()
        []

        """
        logger.info('copy registry hives')
        l_registry_file_infos_copied = list()
        l_registry_file_infos = self.get_l_registry_file_infos()

        for registry_file_info in l_registry_file_infos:
            logger.info('save registry hive {}'.format(registry_file_info.hive_name))
            # noinspection PyBroadException
            try:
                self.copy_registry_file(registry_file_info=registry_file_info)
                l_registry_file_infos_copied.append(registry_file_info)
            except Exception:
                logger.error('can not write {}, needs to run as Administrator'.format(registry_file_info.filename))
        return l_registry_file_infos_copied

    def get_l_registry_file_infos(self)->[lib_data_structures.DataStructRegistryFileInfo]:
        """
        >>> fingerprint_registry = FingerPrintRegistry()
        >>> fp_conf.f_output = 'c:/test/test.csv'
        >>> registry_file_infos = fingerprint_registry.get_l_registry_file_infos()
        >>> registry_file_infos  # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
        [<lib_data_structures.DataStructRegistryFileInfo object at ...>, ...]
        >>> registry_file_infos[0].filename
        'c:/test/test_registry_hklm_sam.hive'
        >>> registry_file_infos[0].hive_name
        'HKLM\\\\SAM'
        >>> registry_file_infos[0].comment
        'HKEY_LOCAL_MACHINE\\\\SAM'

        """
        l_registry_file_infos = list()
        l_hives = self.get_l_hives()
        for registry_hive_name, comment in l_hives:
            registry_file_info = self.get_registry_file_info(registry_hive_name, comment)
            l_registry_file_infos.append(registry_file_info)
        return l_registry_file_infos

    def get_registry_file_info(self, registry_hive_name:str, comment:str)->lib_data_structures.DataStructRegistryFileInfo:
        """
        >>> fingerprint_registry = FingerPrintRegistry()
        >>> fp_conf.f_output = 'c:/test/test.csv'
        >>> registry_file_info = fingerprint_registry.get_registry_file_info('HKLM\\SOFTWARE', 'HKEY_LOCAL_MACHINE\\SOFTWARE')
        >>> registry_file_info.filename
        'c:/test/test_registry_hklm_software.hive'
        >>> registry_file_info.hive_name
        'HKLM\\\\SOFTWARE'
        >>> registry_file_info.comment
        'HKEY_LOCAL_MACHINE\\\\SOFTWARE'
        """
        registry_file_info = lib_data_structures.DataStructRegistryFileInfo()
        registry_file_info.filename = self.get_registry_hive_copy_filename(registry_hive_name)
        registry_file_info.hive_name = registry_hive_name
        registry_file_info.comment = comment
        return registry_file_info

    @staticmethod
    def delete_hive_copies(registry_files_copied):
        logger.info('delete registry hive copies')
        for registry_file_info in registry_files_copied:
            os.remove(registry_file_info.filename)

    def get_l_hives(self)->[()]:
        """

        >>> fingerprint_registry = FingerPrintRegistry()
        >>> fingerprint_registry.get_l_hives()  # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
        [('HKLM\\\\SAM', 'HKEY_LOCAL_MACHINE\\\\SAM'), ('HKLM\\\\SECURITY', 'HKEY_LOCAL_MACHINE\\\\SECURITY'), ...]

        """
        l_hives = [('HKLM\\SAM', 'HKEY_LOCAL_MACHINE\\SAM'),
                   ('HKLM\\SECURITY', 'HKEY_LOCAL_MACHINE\\SECURITY'),
                   ('HKLM\\SOFTWARE', 'HKEY_LOCAL_MACHINE\\SOFTWARE'),
                   ('HKLM\\SYSTEM', 'HKEY_LOCAL_MACHINE\\SYSTEM'),
                   ('HKCR', 'HKEY_CLASSES_ROOT'),
                   ('HKCU', 'HKEY_CURRENT_USER'),
                   ('HKCC', 'HKEY_CURRENT_CONFIGURATION')
                   ]
        l_user_hives = self.get_l_user_hives()
        l_hives = l_hives + l_user_hives
        return l_hives

    @staticmethod
    def get_l_user_hives()->[()]:
        """
        >>> fingerprint_registry = FingerPrintRegistry()
        >>> fingerprint_registry.get_l_user_hives() # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
        [('HKU\\\\.DEFAULT', 'HKEY_USERS\\\\.DEFAULT'), ...]

        """
        ls_user_sids = lib_registry.get_ls_user_sids()
        l_hives = []
        for user_sid in ls_user_sids:
            hive = 'HKU\\{}'.format(user_sid)
            comment = 'HKEY_USERS\\{}'.format(user_sid)
            username = lib_registry.get_username_from_sid(sid=user_sid)
            if username:
                comment = comment + ' ({})'.format(username)
            l_hives.append((hive, comment))
        return l_hives

    @staticmethod
    def copy_registry_file(registry_file_info:lib_data_structures.DataStructRegistryFileInfo):
        """
        >>> fp_conf.f_output = 'c:/testfiles/test_öäüß€_reg.csv'
        >>> fingerprint_registry = FingerPrintRegistry()
        >>> registry_file_info = fingerprint_registry.get_l_registry_file_infos()[0]
        >>> # Error in Doctest because we dont have admin rights
        >>> fingerprint_registry.copy_registry_file(registry_file_info = registry_file_info)  # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
        Traceback (most recent call last):
            ...
        subprocess.CalledProcessError: Command 'reg save HKLM\SAM c:/testfiles/test_öäüß€_reg_registry_hklm_sam.hive /y ' returned non-zero exit status 1.

        >>> fp_conf.f_output = './testfiles/test_öäüß€_reg.csv'
        >>> fingerprint_registry = FingerPrintRegistry()
        >>> registry_file_info = fingerprint_registry.get_l_registry_file_infos()[0]
        >>> # Error in Doctest because we dont have admin rights
        >>> fingerprint_registry.copy_registry_file(registry_file_info = registry_file_info)  # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
        Traceback (most recent call last):
            ...
        subprocess.CalledProcessError: Command 'reg save HKLM\SAM ./testfiles/test_öäüß€_reg_registry_hklm_sam.hive /y ' returned non-zero exit status 1.

        """
        lib_runcommand.run_command('reg save {} '.format(registry_file_info.hive_name) + registry_file_info.filename + ' /y ' + fp_reg_conf.reg_save_additional_parameters)

    def get_registry_hive_copy_filename(self, registry_hive_name):
        """
        :param registry_hive_name:
        :return:

        >>> fingerprint_registry = FingerPrintRegistry()
        >>> fp_conf.f_output = 'c:/test/test.csv'
        >>> fingerprint_registry.get_registry_hive_copy_filename(registry_hive_name='HKLM')
        'c:/test/test_registry_hklm.hive'
        >>> fingerprint_registry.get_registry_hive_copy_filename(registry_hive_name='HKLM\\SYSTEM')
        'c:/test/test_registry_hklm_system.hive'
        """
        f_out_short_name = self.get_f_out_short_name()
        f_out_dir = self.get_f_out_dir()
        hive_name_filename = registry_hive_name.replace('\\', '_').lower()
        registry_filename = '{}/{}_registry_{}.hive'.format(f_out_dir, f_out_short_name, hive_name_filename)
        return registry_filename

    @staticmethod
    def get_f_out_short_name()->str:
        """
        >>> fingerprint_registry = FingerPrintRegistry()
        >>> fp_conf.f_output = './test/test.csv'
        >>> fingerprint_registry.get_f_out_short_name()
        'test'
        """
        f_out_basename:str = os.path.basename(fp_conf.f_output)
        f_out_name = f_out_basename.rsplit('.',1)[0]
        return f_out_name

    @staticmethod
    def get_f_out_dir()->str:
        """
        >>> fingerprint_registry = FingerPrintRegistry()
        >>> fp_conf.f_output = './test/test.csv'
        >>> fingerprint_registry.get_f_out_dir()
        './test'
        """
        f_out_dir = os.path.dirname(fp_conf.f_output)
        return f_out_dir
