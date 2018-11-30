import chardet
import locale
import platform
import subprocess

system_is_windows = platform.system().lower() == 'windows'    # wenn es Windows ist
system_is_linux = platform.system().lower() == 'linux'        # wenn es Linux ist
system_is_darwin = platform.system().lower() == 'darwin'      # wenn es OSX ist


def detect_encoding(raw_bytes)->str:
    detected = chardet.detect(raw_bytes)
    encoding:str = detected['encoding']
    confidence:float = detected['confidence']
    # locale.getpreferredencoding sometimes reports cp1252, but is cp850, so check with chcp
    if system_is_windows and confidence < 0.9:
        encoding = get_encoding()
    return encoding

def get_encoding()->str:
    if system_is_linux or system_is_darwin:
        return get_encoding_linux()
    elif system_is_windows:
        return get_encoding_windows()
    else:
        raise RuntimeError('Operating System {} not supported'.format(platform.system()))

def get_encoding_linux()->str:
    os_encoding = locale.getpreferredencoding()
    return os_encoding

def get_encoding_windows()->str:
    """
    >>> get_encoding_windows()
    'cp850'
    """

    # you might add more encodings, see https://docs.python.org/2.4/lib/standard-encodings.html
    encodings = [('437', 'cp437'),     # United states
                 ('850', 'cp850'),     # Multilingual Latin1
                 ('852', 'cp852'),     # Slavic (Latin II)
                 ('855', 'cp855'),     # Cyrillic (Russian)
                 ('857', 'cp857'),     # Turkish
                 ('860', 'cp860'),     # Portuguese
                 ('861', 'cp861'),     # Icelandic
                 ('863', 'cp863'),     # Canadian-French
                 ('865', 'cp865'),     # Nordic
                 ('860', 'cp860'),     # Portuguese
                 ('866', 'cp866'),     # Russian
                 ('869', 'cp869'),     # Modern Greek
                 ('860', 'cp860'),     # Portuguese
                 ('1252', 'cp1252'),   # West European Latin
                 ('65000', 'utf7'),    # all languages
                 ('65001', 'utf8')     # all languages
                 ]

    # locale.getpreferredencoding sometimes reports cp1252, but is cp850, so check with chcp (especially when shell=True)
    os_encoding = locale.getpreferredencoding()
    completed_process = subprocess.run('chcp', shell=True, capture_output=True)
    chcp_response = completed_process.stdout.decode(os_encoding)
    for encoding_number, encoding in encodings:
        if encoding_number in chcp_response:
            return encoding
    raise RuntimeError('can not detect encoding reported by "chcp" {}'.format(chcp_response))
