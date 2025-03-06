#!/usr/bin/env python3
import sys

from modules.log import *
from modules.env_var import *
from modules.files_worker import *
from modules.downloader import *
from modules.source_fetcher import *

# переменные которые вынесем в отельный файл, аля var
plugins_ver = "20"
libs_ver = "52"
# конец, аля var

work_path = get_env_var("USER_WORK_PATH")

data_path = work_path + "/data"

dist_path = data_path + "/dist"
tmp_path = data_path + "/tmp"
img_path = data_path + "/img"

vulkan_path = data_path + "/vulkan"
plugins_path = data_path + "/plugins_v" + plugins_ver
libs_path = data_path + "/libs_v" + libs_ver

create_new_dir(dist_path, tmp_path, img_path, vulkan_path)

if __name__ == "__main__":
    # TODO: реализовать все функции get_* в модуль downloader.py:

    if len(sys.argv) > 1:  # Проверяем, что есть хотя бы один аргумент (кроме имени скрипта)
        match sys.argv[1]:  # Игнорируем первый аргумент (имя скрипта)
            case "--get-wine": 
                # без аргументов сохраняем список доступных в tmp_path/get_wine.tmp и выводим в терминал
                # если есть аргумент (например WINE_LG_10-1) то обновляем и парсим tmp_path/get_wine.tmp с последующим скачиванием
                get_sources(sys.argv[2:], tmp_path, dist_path)
            case "--get-dxvk":
                # без аргументов сохраняем список доступных в tmp_path/get_dxvk.tmp и выводим в терминал
                # если есть аргумент (например 2.5.3-31) то обновляем и парсим tmp_path/get_dxvk.tmp с последующим скачиванием
                get_dxvk(sys.argv[2:])
            case "--get-vkd3d":
                # без аргументов сохраняем список доступных в tmp_path/get_dxvk.tmp и выводим в терминал
                # если есть аргумент (например 1.1-4367) то обновляем и парсим tmp_path/get_dxvk.tmp с последующим скачиванием
                get_vkd3d(sys.argv[2:])
            case "--get-plugins":
                # версия плагинов будет захардкожена, парсить ничего не надо
                get_plugins(plugins_ver)
            case "--get-libs":
                # версия контейнера будет захардкожена, парсить ничего не надо
                get_libs(libs_ver)

    log.info(work_path)
    log.info(sys.argv[1:])
