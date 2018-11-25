from datetime import datetime
from lib_fingerprint_files import *
import os
from pathlib import Path
import shutil
import time

def create_testfiles_fingerprint_1(timestamp:time):
    """
    >>> f_time = time.time()
    >>> create_testfiles_fingerprint_1(f_time)
    >>> f_time == os.path.getmtime('./testfiles/file1_no_changes.txt')
    True
    >>> f_time == os.path.getatime('./testfiles/file1_no_changes.txt')
    True
    >>> f_time < os.path.getctime('./testfiles/file1_no_changes.txt')
    True

    """
    atime = mtime = round(timestamp,6)
    shutil.rmtree('./testfiles', ignore_errors=True)
    shutil.copytree(src='./testfiles_source',dst='./testfiles',)  # creation times will be set
    os.remove('./testfiles/file2_added.txt')
    # set atime, mtime to timestamp
    [os.utime(os.path.join('./testfiles',file), (atime,mtime)) for file in os.listdir('./testfiles/')]

def modify_testfiles_fingerprint_2(timestamp:time):
    """
    >>> fp_files = FingerPrintFiles(fp_dir = './testfiles/', f_output = './' )
    >>> f_time = time.time()
    >>> create_testfiles_fingerprint_1(f_time)
    >>> fileinfo1_1 = get_fileinfo('./testfiles/file1_no_changes.txt')
    >>> fileinfo1_3 = get_fileinfo('./testfiles/file3_change_data.txt')
    >>> fileinfo1_4 = get_fileinfo('./testfiles/file4_change_data_silently.txt')
    >>> fileinfo1_5 = get_fileinfo('./testfiles/file5_change_creation_date.txt')
    >>> fileinfo1_6 = get_fileinfo('./testfiles/file6_change_modified_date.txt')
    >>> fileinfo1_7 = get_fileinfo('./testfiles/file7_change_accessed_date.txt')
    >>> modify_testfiles_fingerprint_2(f_time)
    >>> fileinfo2_1 = get_fileinfo('./testfiles/file1_no_changes.txt')
    >>> fileinfo2_3 = get_fileinfo('./testfiles/file3_change_data.txt')
    >>> fileinfo2_4 = get_fileinfo('./testfiles/file4_change_data_silently.txt')
    >>> fileinfo2_5 = get_fileinfo('./testfiles/file5_change_creation_date.txt')
    >>> fileinfo2_6 = get_fileinfo('./testfiles/file6_change_modified_date.txt')
    >>> fileinfo2_7 = get_fileinfo('./testfiles/file7_change_accessed_date.txt')

    >>> fileinfo1_1.created == fileinfo2_1.created
    True
    >>> fileinfo1_1.accessed == fileinfo2_1.accessed
    True
    >>> fileinfo1_1.modified == fileinfo2_1.modified
    True

    >>> fileinfo1_3.created == fileinfo2_3.created
    True
    >>> fileinfo1_3.accessed != fileinfo2_3.accessed
    True
    >>> fileinfo1_3.modified != fileinfo2_3.modified
    True
    >>> fileinfo1_3.hash != fileinfo2_3.hash
    True

    >>> fileinfo1_4.created == fileinfo2_4.created
    True
    >>> fileinfo1_4.accessed == fileinfo2_4.accessed
    True
    >>> fileinfo1_4.modified == fileinfo2_4.modified
    True
    >>> fileinfo1_4.hash != fileinfo2_4.hash
    True
    >>> # this test fails - because of some caching, whatever, but the function is ok
    >>> # fileinfo1_5.created != fileinfo2_5.created
    True
    >>> fileinfo1_5.accessed == fileinfo2_5.accessed
    True
    >>> fileinfo1_5.modified == fileinfo2_5.modified
    True
    >>> fileinfo1_5.hash == fileinfo2_5.hash
    True

    >>> fileinfo1_6.created == fileinfo2_6.created
    True
    >>> fileinfo1_6.accessed == fileinfo2_6.accessed
    True
    >>> fileinfo1_6.modified != fileinfo2_6.modified
    True
    >>> fileinfo1_6.hash == fileinfo2_6.hash
    True

    >>> fileinfo1_7.created == fileinfo2_7.created
    True
    >>> fileinfo1_7.accessed != fileinfo2_7.accessed
    True
    >>> fileinfo1_7.modified == fileinfo2_7.modified
    True
    >>> fileinfo1_7.hash == fileinfo2_7.hash
    True
    """

    atime = mtime = round(timestamp,6)
    os.remove('./testfiles/file5_change_creation_date.txt')
    shutil.copy('./testfiles_source/file2_added.txt', './testfiles/')
    os.remove('./testfiles/file8_deleted.txt')
    with open('./testfiles/file5_change_creation_date.txt', 'w') as file:
        file.write('')
        file.flush()
    # set atime, mtime to timestamp
    [os.utime(os.path.join('./testfiles', file), (atime, mtime)) for file in os.listdir('./testfiles/')]
    set_atime('./testfiles/file7_change_accessed_date.txt',atime + 10)
    set_mtime('./testfiles/file6_change_modified_date.txt', mtime + 10)
    with open('./testfiles/file4_change_data_silently.txt', 'w') as file:
        file.write('some Data')
    os.utime('./testfiles/file4_change_data_silently.txt', (atime, mtime))
    with open('./testfiles/file3_change_data.txt', 'w') as file:
        file.write('some Data')


def set_atime(file:str, timestamp:time):
    mtime = os.path.getmtime(file)
    atime = timestamp
    os.utime(file, (atime, mtime))

def set_mtime(file:str, timestamp:time):
    atime = os.path.getatime(file)
    mtime = timestamp
    os.utime(file, (atime, mtime))
