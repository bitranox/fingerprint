import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'fingerprint'))

import lib_hash


def test_get_file_hash_empty_file(tmp_path):
    target = tmp_path / 'empty.bin'
    target.write_bytes(b'')
    assert lib_hash.get_file_hash(str(target)) == \
        'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'


def test_get_file_hash_known_content(tmp_path):
    target = tmp_path / 'hello.txt'
    target.write_bytes(b'hello')
    assert lib_hash.get_file_hash(str(target)) == \
        '2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824'
