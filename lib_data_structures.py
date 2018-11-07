from lib_helper_functions import *

class DataStructFileInfo(object):
    def __init__(self):
        self.path:str = ''
        self.size:int = 0
        self.created:datetime = datetime(1980, 1, 1, 0, 0, 0)
        self.modified:datetime = datetime(1980, 1, 1, 0, 0, 0)
        self.accessed: datetime = datetime(1980, 1, 1, 0, 0, 0)
        self.status:str = ''
        self.change:str = ''    # ADDED, DELETED, MODIFIED (only filled in DIFF Files)
        self.hash:str = ''

    @property
    def set_created(self):
        return None

    @set_created.setter
    def set_created(self,f_created:float):
        self.created = convert_timestamp_to_datetime(f_created)

    @property
    def set_modified(self):
        return None

    @set_modified.setter
    def set_modified(self,f_modified:float):
        self.modified = convert_timestamp_to_datetime(f_modified)

    @property
    def set_accessed(self):
        return None

    @set_accessed.setter
    def set_accessed(self,f_accessed:float):
        self.accessed = convert_timestamp_to_datetime(f_accessed)

    def get_data_dict(self)->dict:
        data_dict = dict()
        data_dict['path'] = self.path
        data_dict['size'] = self.size
        data_dict['created'] = self.created
        data_dict['modified'] = self.modified
        data_dict['accessed'] = self.accessed
        data_dict['status'] = self.status
        data_dict['change'] = self.change
        data_dict['hash'] = self.hash
        return data_dict

    """
    # interessante option nur Setter zu setzen :
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
        self.filename:str = ''
        self.hive_name:str = ''
        self.comment:str = ''

class DataStructRegistryValue(object):
    def __init__(self):
        self.name:str = ''
        self.type:str = ''
        self.value = None

class DataStructRegistryEntry(object):
    def __init__(self):
        self.path:str = ''
        self.modified: datetime = datetime(1980, 1, 1, 0, 0, 0)
        self.l_registry_values:[DataStructRegistryValue] = list()
