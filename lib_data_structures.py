from datetime import datetime
import time
import lib_doctest_pycharm
import lib_helper_functions


lib_doctest_pycharm.setup_doctest_logger_for_pycharm()


class DataStructFileInfo(object):
    def __init__(self):
        """
        >>> ## DataStructFileInfo creation
        >>> import time
        >>> fileinfo = DataStructFileInfo()

        >>> ### created_float, created - setters and getters
        >>> time_float = round(time.time(),6)
        >>> time_datetime = lib_helper_functions.convert_float_to_datetime(time_float)
        >>> fileinfo.created_float = time_float
        >>> time_float == fileinfo.created_float
        True
        >>> time_datetime == fileinfo.created
        True
        >>> time_float = round(time.time(),6)
        >>> time_datetime = lib_helper_functions.convert_float_to_datetime(time_float)
        >>> fileinfo.created = time_datetime
        >>> fileinfo.created_float == time_float
        True
        >>> ### modified_float, crated - setters and getters
        >>> time_float = round(time.time(),6)
        >>> time_datetime = lib_helper_functions.convert_float_to_datetime(time_float)
        >>> fileinfo.modified_float = time_float
        >>> time_float == fileinfo.modified_float
        True
        >>> time_datetime == fileinfo.modified
        True
        >>> time_float = round(time.time(),6)
        >>> time_datetime = lib_helper_functions.convert_float_to_datetime(time_float)
        >>> fileinfo.modified = time_datetime
        >>> fileinfo.modified_float == time_float
        True
        >>> ### accessed_float, accessed - setters and getters
        >>> time_float = round(time.time(),6)
        >>> time_datetime = lib_helper_functions.convert_float_to_datetime(time_float)
        >>> fileinfo.accessed_float = time_float
        >>> time_float == fileinfo.accessed_float
        True
        >>> time_datetime == fileinfo.accessed
        True
        >>> time_float = round(time.time(),6)
        >>> time_datetime = lib_helper_functions.convert_float_to_datetime(time_float)
        >>> fileinfo.accessed = time_datetime
        >>> fileinfo.accessed_float == time_float
        True


        """
        self.path:str = ''
        self.size:int = 0
        self._created_float:float = 0.0
        self._created:datetime = datetime(1980, 1, 1, 0, 0, 0)
        self._modified_float:float = 0.0
        self._modified:datetime = datetime(1980, 1, 1, 0, 0, 0)
        self._accessed_float: float = 0.0
        self._accessed: datetime = datetime(1980, 1, 1, 0, 0, 0)
        self.hash:str = ''
        self.change:str = ''    # ADDED, DELETED, CHANGED, CHANGED_SILENT (Data changed without updating the Filedates)
        self.remark:str = ''

    @property
    def created_float(self)->float:
        return self._created_float

    @created_float.setter
    def created_float(self, created:float):
        self._created_float = created
        self._created = lib_helper_functions.convert_float_to_datetime(created)

    @property
    def created(self)->datetime:
        return self._created

    @created.setter
    def created(self,created:datetime):
        self._created = created
        self._created_float = lib_helper_functions.convert_datetime_to_float(created)

    @property
    def modified_float(self)->float:
        return self._modified_float

    @modified_float.setter
    def modified_float(self, modified:float):
        self._modified_float = modified
        self._modified = lib_helper_functions.convert_float_to_datetime(modified)

    @property
    def modified(self)->datetime:
        return self._modified

    @modified.setter
    def modified(self,modified:datetime):
        self._modified = modified
        self._modified_float = lib_helper_functions.convert_datetime_to_float(modified)

    @property
    def accessed_float(self)->float:
        return self._accessed_float

    @accessed_float.setter
    def accessed_float(self, accessed:float):
        self._accessed_float = accessed
        self._accessed = lib_helper_functions.convert_float_to_datetime(accessed)

    @property
    def accessed(self)->datetime:
        return self._accessed

    @accessed.setter
    def accessed(self,accessed:datetime):
        self._accessed = accessed
        self._accessed_float = lib_helper_functions.convert_datetime_to_float(accessed)

    def get_data_dict(self)->dict:
        """
        >>> import time
        >>> fileinfo = DataStructFileInfo()
        >>> fileinfo.path = 'c:\\path'
        >>> fileinfo.size = 123456
        >>> time_created_float = round(time.time(),6)
        >>> time_modified_float = time_created_float +1
        >>> time_accessed_float = time_created_float +2
        >>> time_created = lib_helper_functions.convert_float_to_datetime(time_created_float)
        >>> time_modified = lib_helper_functions.convert_float_to_datetime(time_modified_float)
        >>> time_accessed = lib_helper_functions.convert_float_to_datetime(time_accessed_float)
        >>> fileinfo.created_float = time_created_float
        >>> fileinfo.modified_float = time_modified_float
        >>> fileinfo.accessed_float = time_accessed_float
        >>> fileinfo.hash = 'hash12345'
        >>> fileinfo.change = 'CHANGED'
        >>> fileinfo.remark = 'Remark'
        >>> data_dict =fileinfo.get_data_dict()
        >>> data_dict['path'] == fileinfo.path == 'c:\\path'
        True
        >>> data_dict['size'] == fileinfo.size == 123456
        True
        >>> data_dict['created'] == fileinfo.created == time_created
        True
        >>> data_dict['modified'] == fileinfo.modified == time_modified
        True
        >>> data_dict['accessed'] == fileinfo.accessed == time_accessed
        True
        >>> data_dict['hash'] == fileinfo.hash == 'hash12345'
        True
        >>> data_dict['change'] == fileinfo.change == 'CHANGED'
        True
        >>> data_dict['remark'] == fileinfo.remark == 'Remark'
        True
        """
        data_dict = dict()
        data_dict['path'] = self.path
        data_dict['size'] = self.size
        data_dict['created'] = self._created
        data_dict['modified'] = self._modified
        data_dict['accessed'] = self._accessed
        data_dict['hash'] = self.hash
        data_dict['change'] = self.change
        data_dict['remark'] = self.remark

        return data_dict

    def get_data_dict_fieldnames(self):
        """
        >>> fileinfo = DataStructFileInfo()
        >>> fileinfo.get_data_dict_fieldnames()
        ['path', 'size', 'created', 'modified', 'accessed', 'hash', 'change', 'remark']
        """
        l_fieldnames = list(self.get_data_dict().keys())
        return l_fieldnames

    """
    # interesting option only to modify the setter :
    # https://stackoverflow.com/questions/17576009/python-class-property-use-setter-but-evade-getter
        def __setattr__(self, name, value):
        if name == 'var':
            print "Setting var!"
            # do something with `value` here, like you would in a
            # setter.
            value = 'Set to ' + value
        super(MyClass, self).__setattr__(name, value)
    """

class DataStructRegistryFileInfo(object):
    def __init__(self):
        """
        >>> reg_file_info = DataStructRegistryFileInfo()
        """
        self.filename:str = ''
        self.hive_name:str = ''
        self.comment:str = ''

class DataStructRegistryValue(object):
    def __init__(self):
        """
        >>> reg_value = DataStructRegistryValue()
        """
        self.name:str = ''
        self.type:str = ''
        self.value = None

class DataStructRegistryEntry(object):
    def __init__(self):
        """
        >>> reg_entry = DataStructRegistryEntry()
        """
        self.path:str = ''
        self.modified: datetime = datetime(1980, 1, 1, 0, 0, 0)
        self.l_registry_values:[DataStructRegistryValue] = list()
