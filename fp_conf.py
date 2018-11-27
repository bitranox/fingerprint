class FPConf(object):
    def __init__(self):
        self.version:str = '2.0.1 Prerelease'
        self.interactive: bool = True

class FPFilesConf(object):
    def __init__(self):
        self.fp_dir:str = ''
        self.f_output:str = ''
        self.exit_if_not_admin:bool = True
        self.hash_files:bool = True
        self.multiprocessing:bool = True

class FPDiffFilesConf(object):
    def __init__(self):
        self.fp1_path:str = ''
        self.fp2_path: str = ''
        self.f_output:str = ''
        self.logfile_fullpath:str = ''


fp_conf = FPConf()
fp_files_conf = FPFilesConf()
fp_diff_files_conf = FPDiffFilesConf()
