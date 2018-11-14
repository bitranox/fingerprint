class FPFilesDiffConf(object):
    def __init__(self):
        self.fp1_path:str = ''
        self.fp2_path: str = ''
        self.fp_result_filename:str = ''
        self.interactive:bool = True
        self.logfile_fullpath:str = ''


fp_files_diff_conf = FPFilesDiffConf()
