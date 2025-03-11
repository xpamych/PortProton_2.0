#!/usr/bin/env python3
import sys

from modules.logger import *
from modules.files_worker import *
from modules.downloader import *
from modules.init_wine import *
from modules.source_fetcher import *
from modules.env_var import *

if __name__ == "__main__":
    if get_env_var("DEBUG") == "1":
        log.setLevel(set_logging_level("DEBUG"))
    else:
        log.setLevel(set_logging_level("INFO"))
    
    log.debug(f"принятые аргументы: {sys.argv[1:]}")
    create_new_dir(dist_path, tmp_path, img_path, vulkan_path)

    if len(sys.argv) > 1:  # Проверяем, что есть хотя бы один аргумент (кроме имени скрипта)
        match sys.argv[1]:  # Игнорируем первый аргумент (имя скрипта)
            case "--get-wine": 
                if sys.argv[2] == "list":
                    get_sources("wine", "list")
                else:
                    get_sources("wine", sys.argv[3:])
            case "--get-dxvk":
                if sys.argv[2] == "list":
                    get_sources("dxvk", "list")
                else:
                    get_sources("dxvk", sys.argv[3:])
            case "--get-vkd3d":
                if sys.argv[2] == "list":
                    get_sources("vkd3d", "list")
                else:
                    get_sources("vkd3d", sys.argv[3:])
    
    log.info("INFO")

    # init_wine("WINE_LG_9-2")
    # get_sources(["proton-cachyos-9.0-20250126-slr-x86_64_v3"])
    # get_sources([""])
