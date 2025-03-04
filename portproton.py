#!/usr/bin/env python3

from modules.log import *
from modules.env_var import *
from modules.files_worker import *
from modules.downloader import *

data_path = get_env_var("DATA_PATH")
work_path = get_env_var("WORK_PATH")

if __name__ == "__main__":

    log.info(data_path)
    log.info(work_path)
    log.info(sys.argv[1:])