import filecmp
import hashlib
import json
import logging
import os
import shutil
import tarfile
import tempfile

import requests

from samba.samba3.smbd import create_file

from .env_var import *
from .config_parser import *
from .logger import *

# константы:
tmp_path = tempfile.gettempdir() + "/portproton"
work_path = get_env_var("USER_WORK_PATH")
data_path = work_path + "/data"
dist_path = data_path + "/dist"
img_path = data_path + "/img"
vulkan_path = data_path + "/vulkan"
plugins_path = data_path + "/plugins_v" + var("plugins_ver")
libs_path = data_path + "/libs_v" + var("libs_ver")

log.info(f"рабочий каталог: {work_path}")

def try_copy_file(source, destination):  # функция копирования если файлы различаются
    if not os.path.exists(source):
        raise FileNotFoundError (f"file not found for copy: {source}")
        return False

    if os.path.exists(destination):
        if filecmp.cmp(source, destination, shallow=False):
            return True

    if shutil.copy2(source, destination):
        return True
    else:
        return False

def try_force_link_file(source, link):
    if not os.path.exists(source):
        raise FileNotFoundError (f"file not found for link: {source}")
        return False

    try:
        if os.path.exists(link) or os.path.islink(link):
            os.remove(link)

        os.symlink(source, link)
    except Exception as e:
        log.error(f"failed to create link for file: {e}")


def try_remove_file(file_path):
    if os.path.exists(file_path) and os.path.isfile(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            log.error(f"failed to remove file: {e}")

def create_new_dir(*path):
    for i in path:
        if not os.path.exists(i):
            try:
                os.makedirs(i)
            except Exception as e:
                log.error(f"failed to create directory: {e}")

def try_force_link_dir(path, link):
    if not os.path.exists(path):
        raise FileNotFoundError (f"directory not found for link: {path}")
        return False

    try:
        if os.path.exists(link) or os.path.islink(link):
            os.remove(link)

        os.symlink(path, link)
    except Exception as e:
        log.error(f"failed to create link for file: {e}")

def try_move_dir(src, dst): # Перемещает каталог src в dst, заменяя существующие файлы.
    for src_dir, dirs, files in os.walk(src):
        dst_dir = src_dir.replace(src, dst, 1)
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
        for file_ in files:
            src_file = os.path.join(src_dir, file_)
            dst_file = os.path.join(dst_dir, file_)
            if os.path.exists(dst_file):
                if os.path.samefile(src_file, dst_file):
                    continue
                os.remove(dst_file)
            shutil.move(src_file, dst_dir)
    try_remove_dir(src)

def replace_file(file_path, file_name): # функция замены файла (сначала запись во временный файл, потом замена)
    try:
        if os.path.exists(file_name) and os.path.getsize(file_name) > 0:
            os.replace(file_name, file_path)  # Меняем местами файлы, если временный файл не пуст
            log.info(f"Данные успешно обновлены в {file_path}.")
        else:
            log.warning(f"Временный файл {file_name} пуст, замена в {file_path} не выполнена.")
            if os.path.exists(file_name):
                os.remove(file_name)  # Удаляем пустой временный файл
    except Exception as e:
        log.error(f"Ошибка при замене файла: {e}")

def try_write_temp_file(file_path, file_name):  # функция записи в tmp
    try:
        with open(file_path, 'w') as file:
            file.write("\n".join(file_name))  # Записываем все имена файлов во временный файл
    except Exception as e:
        log.error(f"Ошибка при записи во временный файл {file_path}: {e}")

def try_remove_dir(path):
    if os.path.exists(path) and os.path.isdir(path):
        try:
            shutil.rmtree(path)
        except Exception as e:
            log.error(f"failed to remove directory: {e}")

def get_last_modified_time(file_path, fallback=None):  # Добавьте fallback как необязательный параметр
    try:
        return os.path.getmtime(file_path)
    except FileNotFoundError:
        log.warning(f"Файл не найден: {file_path}")
        return fallback  # Возврат значения по умолчанию
    except Exception as e:
        log.error(f"Ошибка при получении времени изменения файла {file_path}: {e}")
        return fallback  # Возврат значения по умолчанию

def load_metadata(metadata_file_path):  # Функция загрузки метаданных из файла
    if os.path.isfile(metadata_file_path):
        with open(metadata_file_path, 'r') as metadata_file:
            return json.load(metadata_file)
    return None

def compute_metadata(archive_path):  # Функция вычисления метаданных из архива
    """Вычисляет метаданные из архива."""
    metadata = []
    with tarfile.open(archive_path, mode="r:*") as tar:
        for member in tar.getmembers():
            if member.isfile():  # Если это файл
                file_info = {
                    "name": member.name,
                    "size": member.size,
                    "modified_time": member.mtime,
                    "extracted_path": member.name  # Путь без директории для сравнения
                }
                metadata.append(file_info)
    return metadata

def check_free_space(directory, required_space): # Функция проверки свободного места
    statvfs = os.statvfs(directory)
    free_space = statvfs.f_frsize * statvfs.f_bavail
    return free_space >= required_space

def get_archive_size(archive_path): # Функция получения размера архива
    total_size = 0
    with tarfile.open(archive_path, mode="r:*") as tar:
        for member in tar.getmembers():
            total_size += member.size
    return total_size

def unpack(archive_path, extract_to=None): # Функция распаковки архива
    if not os.path.isfile(archive_path):
        log.error(f"Архив {archive_path} не найден.")
        return False

    try:
        if extract_to is None:
            log.debug(f"Распаковка файла: {archive_path}")
            extract_to = os.path.join(tmp_path, os.path.dirname(archive_path))
        elif not os.path.isdir(extract_to):
            print(f"Папка для распаковки не существует: {extract_to}")
            create_new_dir(extract_to)

        base_name = os.path.basename(archive_path)
        name_without_extension = os.path.splitext(base_name)[0]

        while name_without_extension.endswith(('.tar', '.gz', '.xz')):
            name_without_extension = os.path.splitext(name_without_extension)[0]

        extracted_directory = os.path.join(extract_to, name_without_extension)

        if not os.path.exists(extracted_directory):
            os.makedirs(extracted_directory)
            log.info(f"Создана директория: {extracted_directory}")

        metadata_file_path = os.path.join(extracted_directory, "metadata.json")  # Путь к метаданным
        new_metadata = compute_metadata(archive_path)  # Вычисляем метаданные из архива

        with open(metadata_file_path, 'w') as metadata_file:
            json.dump(new_metadata, metadata_file, indent=4)
            log.info(f"Метаданные успешно сохранены в {metadata_file_path}")

        required_space = get_archive_size(archive_path)

        if not check_free_space(extracted_directory, required_space):
            log.error("Недостаточно свободного места для распаковки архива.")
            return False

        with tarfile.open(archive_path, mode="r:*") as tar:
            for member in tar.getmembers():

                relative_path = member.name[len(name_without_extension) + 1:]
                extracted_file_path = os.path.join(extracted_directory, relative_path)
                tar.extract(member, path=extract_to)
                set_file_permissions(extracted_file_path)
            log.info(f"Архив {archive_path} успешно распакован в {os.path.realpath(extracted_directory)}")
            return True

    except Exception as e:
        logging.critical(f"Ошибка распаковки ({type(e).__name__}): {e} при работе с файлом {archive_path}")
    return False

def check_hash_sum(check_file, check_sum): # Функция проверки\вычисления хеш-суммы локального файла
    if not os.path.isfile(check_file):
        log.error(f"Файл {check_file} не найден.")
        return False

    if check_sum:
        if len(check_sum) == 64:  # SHA-256
            hash_func = hashlib.sha256()
        elif len(check_sum) == 128:  # SHA-512
            hash_func = hashlib.sha512()
        else:
            log.error("Недопустимая длина ожидаемой хеш-суммы.")
            return False
    else:
        log.error("Хеш-сумма не указана для проверки.")
        return False

    # Считываем содержимое файла и вычисляем хеш-сумму
    with open(check_file, "rb") as f:
        while chunk := f.read(8192):  # Читаем файл частями по 8192 байта
            hash_func.update(chunk)  # Обновляем хеш с новым чанком

    computed_hash = hash_func.hexdigest()  # Получаем вычисленный хеш
    log.debug(f"Вычисленная хеш-сумма: {computed_hash}, ожидаемая: {check_sum}")

    if computed_hash.lower() != check_sum.lower():
        log.error(f"Хеш-суммы не совпадают: ожидаемая {check_sum}, полученная {computed_hash}.")
        return False

    log.info("Проверка хеш-суммы прошла успешно.")
    return True  # Возвращаем True, если хеши совпадают

def compare_directory_with_metadata(dist_path, metadata): # Функция сравнения содержимого директории с метаданными
    all_files_match = True  # Переменная для отслеживания статуса сравнений

    for file_info in metadata:
        extracted_file_path = os.path.join(dist_path, file_info['extracted_path'])

        if not os.path.isfile(extracted_file_path):
            log.warning(f"Файл {extracted_file_path} отсутствует в каталоге.")
            all_files_match = False
            continue

        actual_size = os.path.getsize(extracted_file_path)

        if actual_size != file_info['size']:
            log.warning(f"Несоответствие между файлом {extracted_file_path} и метаданными: "
                        f"ожидаемый размер {file_info['size']}, фактический размер {actual_size}.")
            all_files_match = False

    return all_files_match

def set_file_permissions(file_path): # Функция установки прав доступа к файлу
    try:
        if not os.path.islink(file_path):  # Проверяем, не является ли файл символьной ссылкой
            os.chmod(file_path, 0o755)

    except Exception as e:
        log.error(f"Не удалось установить права для файла {file_path}: {e}")

