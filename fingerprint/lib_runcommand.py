import lib_detect_encoding
import locale
import logging
import os
import re
import subprocess
import sys

logger = logging.getLogger()
locale.setlocale(locale.LC_ALL, '')     # This sets the locale for all categories to the user’s default setting (typically specified in the LANG environment variable).

class CommandResponse(object):
    def __init__(self):
        self.returncode:int = 0
        self.stdout:str = ''
        self.stderr: str = ''

def run_command(s_command:str, shell:bool = False, communicate:bool = True, wait_finish:bool = True, raise_on_error:bool = True)->CommandResponse:
    """
    TODO - LOGGING ON/OF/LEVEL/ETC before use it !!!
    >>> response = run_command('dir c:\python3', shell=True) # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    >>> response.stdout # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE

    >>> response = run_command('dir c:\python3') # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
        ...
    FileNotFoundError: ...

    """
    ls_args = shlex_split_multi_platform(s_command)

    my_env = os.environ.copy()
    my_env['PYTHONIOENCODING'] = 'utf-8'
    my_env['PYTHONLEGACYWINDOWSIOENCODING'] = 'utf-8'

    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW      # HIDE CONSOLE

    my_process = subprocess.Popen(ls_args, startupinfo=startupinfo, stdin=subprocess.PIPE,
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=shell, env=my_env)

    if communicate:
        stdout, stderr = my_process.communicate()
        encoding = lib_detect_encoding.detect_encoding(stdout+stderr)
        stdout = stdout.decode(encoding)
        stderr = stderr.decode(encoding)
        returncode = my_process.returncode
    else:
        stdout = None
        stderr = None
        if wait_finish:
            my_process.wait()
            returncode = my_process.returncode
        else:
            returncode = 0

    if raise_on_error and returncode:
        logger.info(stdout)
        logger.info(stderr)
        raise subprocess.CalledProcessError(returncode=returncode, cmd=s_command, output=stdout, stderr=stderr)

    command_response = CommandResponse()
    command_response.stdout = stdout
    command_response.stderr = stderr
    command_response.returncode = returncode
    return command_response


def shlex_split_multi_platform(s_commandline:str, n_platform:int = None)->[str]:
    """
    Multi-n_platform variant of shlex.split() for command-line splitting.
    For use with subprocess, for argv injection etc. Using fast REGEX.

    its ~10x faster than shlex, which does single-char stepping and streaming;
    and also respects pipe-related characters (unlike shlex).

    from : https://stackoverflow.com/questions/33560364/python-windows-parsing-command-lines-with-shlex


    :param s_commandline :  the command line string to split
    :param n_platform:      None = auto from current n_platform;
                            1 = POSIX;
                            0 = Windows/CMD
                            (other values reserved)

    >>> shlex_split_multi_platform('c:/test.exe /n /r /s=test')
    ['c:/test.exe', '/n', '/r', '/s=test']

    """

    if n_platform is None:
        n_platform = (sys.platform != 'win32')
    if n_platform == 1:
        re_cmd_lex = r'''"((?:\\["\\]|[^"])*)"|'([^']*)'|(\\.)|(&&?|\|\|?|\d?\>|[<])|([^\s'"\\&|<>]+)|(\s+)|(.)'''
    elif n_platform == 0:
        re_cmd_lex = r'''"((?:""|\\["\\]|[^"])*)"?()|(\\\\(?=\\*")|\\")|(&&?|\|\|?|\d?>|[<])|([^\s"&|<>]+)|(\s+)|(.)'''
    else:
        raise AssertionError('unknown n_platform %r' % n_platform)

    args = []
    acc = None   # collects pieces of one arg
    for qs, qss, esc, pipe, word, white, fail in re.findall(re_cmd_lex, s_commandline):
        if word:
            pass   # most frequent
        elif esc:
            word = esc[1]
        elif white or pipe:
            if acc is not None:
                args.append(acc)
            if pipe:
                args.append(pipe)
            acc = None
            continue
        elif fail:
            raise ValueError("invalid or incomplete shell string")
        elif qs:
            word = qs.replace('\\"', '"').replace('\\\\', '\\')
            if n_platform == 0:
                word = word.replace('""', '"')
        else:
            word = qss   # may be even empty; must be last

        acc = (acc or '') + word

    if acc is not None:
        args.append(acc)

    return args
