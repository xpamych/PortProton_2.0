import os
import glob
import re

from .log import *

def main_clear_db():
    base_dir = os.path.dirname(os.path.realpath(__file__))
    portwine_db_path = os.path.join(base_dir, 'portwine_db')
    os.makedirs(portwine_db_path, exist_ok=True)

    for filename in glob.glob(os.path.join(portwine_db_path, '*')):  # Установка разрешений на файлы
        os.chmod(filename, 0o644)

    duplicate_finder = {} #Поиск дубликатов в файлах
    for filename in glob.glob(os.path.join(portwine_db_path, '*')):
        with open(filename, 'r') as file:
            lines = file.readlines()
            for line in lines:
                if '.exe' in line and '#' in line:
                    line = line.strip()
                    if line not in duplicate_finder:
                        duplicate_finder[line] = []
                    duplicate_finder[line].append(filename)

    duplicates = {line: files for line, files in duplicate_finder.items() if len(files) > 1}
    if duplicates:
        log.warning("Обнаружены дубликаты в файлах:")
        for line, files in duplicates.items():
            for file in files:
                log.info(f"{file.split('portwine_db/')[1]} содержит дубликат: {line}")
        exit(1)


    for ppdb in glob.glob(os.path.join(portwine_db_path, '*')):  # Обработка каждого файла
        log.debug(ppdb)

        with open(ppdb, 'r') as file:  # Удаление определённых строк
            lines = file.readlines()

        lines = [line for line in lines if not line.startswith(('##export', '##add_'))]
        lines = [line for line in lines if not (
            re.search(r'MANGOHUD|FPS_LIMIT|VKBASALT|_RAY_TRACING|_DLSS|PW_GUI_DISABLED_CS|PW_USE_GAMEMODE|'
                      r'PW_USE_SYSTEM_VK_LAYERS|PW_DISABLE_COMPOSITING|PW_USE_EAC_AND_BE|PW_USE_OBS_VKCAPTURE|'
                      r'GAMESCOPE|PW_GS', line)
        )]

        if any(re.search(r'PW_USE_DGVOODOO2="0"|PW_DGVOODOO2="0"', line) for line in lines):
            lines = [line for line in lines if not re.search(r'PW_USE_DGVOODOO2|PW_DGV', line)]


        lines = [re.sub(r'export PW_WINE_USE=.*', 'export PW_WINE_USE="WINE_LG"', line)
                 if 'PW_WINE_USE="WINE_LG' in line else line for line in lines]
        lines = [re.sub(r'export PW_WINE_USE=.*', 'export PW_WINE_USE="PROTON_LG"', line)
                 if 'PW_WINE_USE="PROTON_LG' in line else line for line in lines]

        with open(ppdb, 'w') as file:  # Сохранение изменений
            file.writelines(lines)

        ppdb_base = os.path.basename(ppdb)  # Переименование файлов
        if ppdb_base.endswith('.exe.ppdb'):
            new_name = f"{ppdb_base[:-9]}.ppdb"
            os.rename(ppdb, os.path.join(portwine_db_path, new_name))
        elif ppdb_base.endswith('.EXE.ppdb'):
            new_name = f"{ppdb_base[:-9]}.ppdb"
            os.rename(ppdb, os.path.join(portwine_db_path, new_name))
        elif not ppdb_base.endswith('.ppdb'):
            new_name = f"{ppdb_base}.ppdb"
            os.rename(ppdb, os.path.join(portwine_db_path, new_name))

    log.info("ГОТОВО!")
    exit(0)
