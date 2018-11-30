class FPConf(object):
    def __init__(self):
        self.f_output: str = ''
        self.version:str = '2.0.2 Prerelease'
        self.interactive:bool = True

class FPFilesConf(object):
    def __init__(self):
        self.fp_dir:str = ''
        self.exit_if_not_admin:bool = True
        self.hash_files:bool = True
        self.multiprocessing:bool = True

class FPDiffFilesConf(object):
    def __init__(self):
        self.fp1_path:str = ''
        self.fp2_path:str = ''
        self.logfile_fullpath:str = ''

class FPRegConf(object):
    def __init__(self):
        self.field_length_limit:int = 32767
        self.reg_save_additional_parameters:str = ''
        self.delete_hive_copies:bool = True
        self.exit_if_not_admin: bool = True

fp_conf:FPConf = FPConf()
fp_files_conf:FPFilesConf = FPFilesConf()
fp_diff_files_conf:FPDiffFilesConf = FPDiffFilesConf()
fp_reg_conf:FPRegConf = FPRegConf()
