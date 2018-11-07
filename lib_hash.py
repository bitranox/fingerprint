import hashlib

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
    """
    :param fname:
    :return:
    >>> get_file_hash('C:/opt/vm-shared-folder/pyapps/fingerprint/build.py')
    """
    try:
        result = hash_bytestr_iter(file_as_blockiter(open(fname, 'rb')), hashlib.sha256())
        return result
    except Exception:
        return 'Access denied for Hashing'
