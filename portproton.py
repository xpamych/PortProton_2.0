#!/usr/bin/env python3
import sys

from modules.log import *
from modules.files_worker import *
from modules.downloader import *
from modules.init_wine import *
from modules.source_fetcher import *

mirror = True # перенести в функцию как (arg, mirror=True)

log.info(f"принятые аргументы: {sys.argv[1:]}")

if __name__ == "__main__":
    create_new_dir(dist_path, tmp_path, img_path, vulkan_path)

    if len(sys.argv) > 1:  # Проверяем, что есть хотя бы один аргумент (кроме имени скрипта)
        match sys.argv[1]:  # Игнорируем первый аргумент (имя скрипта)
            case "--get-wine": 
                # без аргументов сохраняем список доступных в tmp_path/get_wine.tmp и выводим в терминал
                # если есть аргумент (например WINE_LG_10-1) то обновляем и парсим tmp_path/get_wine.tmp с последующим скачиванием
                get_sources(sys.argv[2:], mirror)
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

    init_wine("WINE_LG")
