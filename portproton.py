#!/usr/bin/env python3
import sys

from modules.log import *
from modules.env_var import *
from modules.files_worker import *
from modules.downloader import *

work_path = get_env_var("USER_WORK_PATH")

data_path = work_path + "/data"

dist_path = data_path + "/dist"
tmp_path = data_path + "/tmp"
img_path = data_path + "/img"

create_new_dir(dist_path)
create_new_dir(tmp_path)
create_new_dir(img_path)

if __name__ == "__main__":

    if len(sys.argv) > 1:  # Проверяем, что есть хотя бы один аргумент (кроме имени скрипта)
        match sys.argv[1]:  # Игнорируем первый аргумент (имя скрипта)
            case "--get-wine":
                # get_wine(sys.argv[2:])
                ...

    log.info(work_path)

    log.info(sys.argv[1:])
