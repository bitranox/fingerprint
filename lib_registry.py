import winreg
from winreg import *

def get_number_of_subkeys(key:HKEYType)->int:
    """
    param key : one of the winreg HKEY_* constants :
                HKEY_CLASSES_ROOT, HKEY_CURRENT_CONFIG, HKEY_CURRENT_USER, HKEY_DYN_DATA,
                HKEY_LOCAL_MACHINE, HKEY_PERFORMANCE_DATA, HKEY_USERS

    >>> get_number_of_subkeys(HKEY_USERS)
    6
    """
    number_of_subkeys, number_of_values, last_modified_win_timestamp = QueryInfoKey(key)
    return number_of_subkeys

def get_ls_user_sids()->[str]:
    """
    >>> get_ls_user_sids()
    ['.DEFAULT', 'S-1-5-18', 'S-1-5-19', 'S-1-5-20', 'S-1-5-21-206651429-2786145735-121611483-1001', 'S-1-5-21-206651429-2786145735-121611483-1001_Classes']

    """
    ls_user_sids = []
    n_sub_keys = get_number_of_subkeys(key=HKEY_USERS)
    for i in range(n_sub_keys):
        subkey = EnumKey(HKEY_USERS,i)
        ls_user_sids.append(subkey)
    return sorted(ls_user_sids)

def get_username_from_sid(sid:str)->str:
    """
    :param sid:
    :return:
    >>> get_username_from_sid(sid='S-1-5-20')
    'NetworkService'
    """
    # noinspection PyBroadException
    try:
        reg = ConnectRegistry(None, HKEY_LOCAL_MACHINE)
        key = OpenKey(reg, r'SOFTWARE\Microsoft\Windows NT\CurrentVersion\ProfileList\{}'.format(sid))
        # value types see https://docs.python.org/3.4/library/winreg.html#value-types
        val, value_type = QueryValueEx(key, 'ProfileImagePath')
        username = val.rsplit('\\',1)[1]
        return username
    except Exception:
        return ''
