from lib_runcommand import run_command
from lib_helper_functions import *
import logging
import time
logger = logging.getLogger()
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s')

# enum34 needs to be uninstalled on python3.7 in order to make pyinstaller work

ls_commands = ['pyinstaller --onefile fingerprint.py -y',
               'pyinstaller --onefile fingerprint_diff.py -y',
               'pyinstaller --onefile fingerprint_filter.py -y']

for s_command in ls_commands:
    response = run_command(s_command)
    logger.info(response.stdout)
    if response.stderr:
        logger.error(response.stderr)

logger_flush_all_handlers()
input('Enter to exit')
