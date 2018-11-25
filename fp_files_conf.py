class FPFilesConf(object):
    def __init__(self):
        self.fp_dir:str = ''
        self.f_output:str = ''
        self.interactive:bool = True
        self.exit_if_not_admin:bool = True
        self.hash_files:bool = True
        self.multiprocessing:bool = True
        self.version:str = '2.0.0'

fp_files_conf = FPFilesConf()
