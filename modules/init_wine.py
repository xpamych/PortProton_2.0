import os
import shutil
import subprocess

from .log import *
from .env_var import *
from .files_worker import *
from .config_parser import *
from .downloader import *

def init_wine(wine_version=None):
    if wine_version is None:
        used_wine = var("used_wine")
    else:
        used_wine = wine_version

    # TODO: будем переименовывать все каталоги wine в верхний регистр?

    if used_wine.upper() != "SYSTEM":
        if used_wine.upper() == "WINE_LG":
            used_wine = var("default_wine")
        elif used_wine.upper() == "PROTON_LG":
            used_wine = var("default_proton")

        wine_path = dist_path + "/" + used_wine

        if not os.path.exists(wine_path + "/bin/wine"):
            log.warning(f"{used_wine} not found. Try download...")

            # TODO: использовать зеркало при необходимости
            # url_github_lg="https://github.com/Castro-Fidel/wine_builds/releases/download/" + used_wine + "/" + used_wine

            url_cloud_lg="https://cloud.linux-gaming.ru/portproton/" + used_wine
            
            if try_download(url_cloud_lg + ".tar.xz") and try_download(url_cloud_lg + ".sha256sum"):
                if check_hash_sum(tmp_path + "/" + used_wine + ".tar.xz", tmp_path + "/" + used_wine + ".sha256sum"):
                    unpack(tmp_path + "/" + used_wine + ".tar.xz", dist_path)
                    for f in [".tar.xz", ".sha256sum"]:
                        try_remove_file(tmp_path + "/" + used_wine + f)

        if not os.path.exists(wine_path + "/bin/wine"):
            log.critical(f"{used_wine} not found. Interrupt!")

        env_var("PATH", wine_path + "/bin")
        env_var("LD_LIBRARY_PATH", wine_path + "/lib")
        set_env_var_force("WINEDLLPATH", wine_path + "/lib/wine")
        if os.path.exists(wine_path + "/lib64/"):
            env_var("LD_LIBRARY_PATH", wine_path + "/lib64")
            env_var("WINEDLLPATH", wine_path + "/lib64/wine")

        wine_share = wine_path + "/share"
        if os.path.exists(wine_share + "/espeak-ng-data/"):
            set_env_var_force("ESPEAK_DATA_PATH", wine_share)
        if os.path.exists(wine_share + "/media/"):
            set_env_var_force("MEDIACONV_BLANK_VIDEO_FILE", wine_share + "/media/blank.mkv")
            set_env_var_force("MEDIACONV_BLANK_AUDIO_FILE", wine_share + "/media/blank.ptna")       

        for wine_utils in ["mono", "gecko"]:
            if not os.path.islink(wine_share + "/wine/" + wine_utils):
                if os.path.isdir(wine_share + "/wine/" + wine_utils):
                    try_move_dir(wine_share + "/wine/" + wine_utils, data_path + "/" + wine_utils)
                try_force_link_dir(data_path + "/" + wine_utils, wine_share + "/wine/" + wine_utils)

    else:
        try:
            result = subprocess.run(['wine', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode == 0:
                log.info(f"Используется системная версия WINE: {result.stdout.strip()}")
                wine_path = "/usr"
            else:
                log.critical("Произошла ошибка во время получения версии системного WINE.")
        except FileNotFoundError:
            log.critical("Команда wine не найдена в системе.")

        
    # общие переменные окружения для любой версии wine
    set_env_var_force("WINE", wine_path + "/bin/wine")
    set_env_var_force("WINELOADER", wine_path + "/bin/wine")
    set_env_var_force("WINESERVER", wine_path + "/bin/wineserver")

    log.info(f"wine in used: {used_wine}")
    print_env_var("WINELOADER", "WINESERVER", "WINEDLLPATH")
    print_env_var("PATH", "LD_LIBRARY_PATH")
    # print_env_var("ESPEAK_DATA_PATH", "MEDIACONV_BLANK_VIDEO_FILE", "MEDIACONV_BLANK_AUDIO_FILE")
