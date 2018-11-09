import hashlib
import os
import time

def hash_bytestr_iter(bytesiter, hasher, ashexstr=True):
    for block in bytesiter:
        hasher.update(block)
    return hasher.hexdigest() if ashexstr else hasher.digest()

def file_as_blockiter(afile, blocksize=65536):
    with afile:
        block = afile.read(blocksize)
        while len(block) > 0:
            yield block
            block = afile.read(blocksize)

def get_file_hash(fname:str):
    result = hash_bytestr_iter(file_as_blockiter(open(fname, 'rb')), hashlib.sha256())
    return result

def get_file_hash_preserve_access_dates(fname:str):
    """
    :param fname:
    :return:
    >>> import os, test, time
    >>> timestamp = time.time()
    >>> test.create_testfiles_fingerprint_1(timestamp)
    >>> atime1 = os.path.getatime('./testfiles/file1_no_changes.txt')
    >>> get_file_hash_preserve_access_dates('./testfiles/file1_no_changes.txt')
    'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
    >>> atime2 = os.path.getatime('./testfiles/file1_no_changes.txt')
    >>> atime1 == atime2
    True
    """
    atime, mtime = get_atime_mtime(fname)   # preserve access and modify dates
    result = get_file_hash(fname)
    set_atime_mtime(fname, atime, mtime)    # preserve access and modify dates
    return result

def get_atime_mtime(f_name:str)->(time.time, time.time):
    atime = os.path.getatime(f_name)
    mtime = os.path.getmtime(f_name)
    return atime, mtime

def set_atime_mtime(f_name:str, atime:time.time, mtime:time.time):
    os.utime(f_name, (atime, mtime))
