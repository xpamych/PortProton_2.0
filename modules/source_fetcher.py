import re
import requests
import time

from modules.downloader import try_download
from modules.files_worker import *

count_wines = 25  # Количество элементов для записи в .tmp файл
repos = {  # Список репозиториев для обработки и их короткие имена
    "GloriousEggroll/proton-ge-custom": "proton-ge-custom",
    "Kron4ek/Wine-Builds": "Kron4ek",
    "GloriousEggroll/wine-ge-custom": "wine-ge-custom",
    "CachyOS/proton-cachyos": "proton-cachyos",
    "Castro-Fidel/wine_builds": "LG"
}

def source_list_checker(tmp_path): # Проверка наличия и обновления файлов со списками исходников
    for repo, short_name in repos.items():
        output_file = os.path.join(tmp_path, f"{short_name}.tmp")

        if not os.path.exists(output_file):
            log.info(f"Файл {output_file} не существует. Получаем данные из репозитория.")
            source_list_downloader(repo, tmp_path, short_name, output_file)
            continue  # Переходим к следующему репозиторию

        if os.path.getsize(output_file) == 0:  # Проверяем, является ли файл пустым
            log.info(f"Файл {output_file} пуст. Обновляем данные.")
            source_list_downloader(repo, tmp_path, short_name, output_file)
            continue  # Переходим к следующему репозиторию

        last_modified_time = get_last_modified_time(output_file) # Получаем время последнего изменения файла
        if last_modified_time is None:  # Если время не удалось получить, пробуем обновить файл
            log.info(f"Не удалось получить время последнего изменения для {output_file}. Попытаемся обновить.")
            source_list_downloader(repo, tmp_path, short_name, output_file)
            continue  # Переходим к следующему репозиторию

        current_time = time.time()

        if current_time - last_modified_time >= 10800:  # 10800 секунд = 3 часа, проверяем, устарел ли файл
            log.info(f"Файл {output_file} устарел. Обновляем данные.")
            source_list_downloader(repo, tmp_path, short_name, output_file)
        else:
            log.info(f"Файл {output_file} существует и был обновлён менее 3 часов назад. Используем кэшированные данные.")

def source_list_downloader(repo, tmp_path, short_name, output_file):
    url = f"https://api.github.com/repos/{repo}/releases?per_page={count_wines}"
    temp_file = os.path.join(tmp_path, f"{short_name}.tmp.new")  # Временный файл

    try:
        response = requests.get(url)
        response.raise_for_status()  # Возбудим исключение для ошибок HTTP
        releases = response.json()

        log.debug(f"Ответ API: {releases}")
        tar_files = []  # Проверяем каждый релиз
        for release in releases:
            assets = release.get('assets', [])
            for asset in assets:
                asset_name = asset['name']
                if (
                        (re.search(r'(wine|proton)', asset_name, re.IGNORECASE) or
                         re.search(r'^GE-Proton\d+-\d+\.tar\.gz$', asset_name) or
                         re.search(r'^GE-Proton\d+(-\d+)?\.tar\.xz$', asset_name)) and
                        (asset_name.endswith('.tar.gz') or asset_name.endswith('.tar.xz'))
                ):
                    tar_files.append(asset_name)  # Собираем все подходящие файлы
                    log.debug(f"Найденный файл: {asset_name}")

        if not tar_files:
            log.warning(f"Нет подходящих файлов в репозитории {repo}.")
            return  # Выходим из функции, если нет файлов

        with open(temp_file, 'w') as file:  # Записываем найденные файлы во временный файл
            file.write("\n".join(tar_files))

        log.info(f"Данные успешно записаны в временный файл {temp_file}.")

        if os.path.exists(temp_file):  # Если запись прошла успешно, заменяем основной файл
            os.replace(temp_file, output_file)
            log.info(f"Файл {output_file} успешно обновлен.")

    except requests.exceptions.RequestException as e:
        log.error(f"Ошибка при получении данных из {repo}: {str(e)}")

def get_sources(args, tmp_path, dist_path):
    os.makedirs(tmp_path, exist_ok=True)
    source_list_checker(tmp_path)

    if args:
        for arg in args:
            for repo, short_name in repos.items():  # определяем короткое имя репозитория
                tmp_file_path = os.path.join(tmp_path, f"{short_name}.tmp")

                if os.path.exists(tmp_file_path):  # проверяем наличие файла
                    with open(tmp_file_path, 'r') as file:
                        all_tar_gz_files = file.read().splitlines()

                    for file_to_download in all_tar_gz_files: # Ищем совпадение в файле
                        if arg in file_to_download:
                            log.info(f"Найдено совпадение для '{arg}': {file_to_download} в файле {tmp_file_path}")
                            url = f"https://github.com/{repo}/releases/latest/download/{file_to_download}" # Получаем URL файла
                            tmp_file = os.path.join(tmp_path, file_to_download)
                            if not os.path.exists(tmp_file):
                                try:
                                    try_download(url, tmp_path)
                                    unpack(tmp_file, dist_path)
                                    try_remove_file(tmp_file)
                                except Exception as e:
                                    log.error(f"Ошибка при загрузке или распаковке: {str(e)}")
