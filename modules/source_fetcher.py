import re
import time

import requests

from modules.downloader import try_download
from modules.files_worker import *

repos = {  # Список репозиториев для обработки и их короткие имена
    "GloriousEggroll/proton-ge-custom": "proton-ge-custom",
    "GloriousEggroll/wine-ge-custom": "wine-ge-custom",
    "Kron4ek/Wine-Builds": "Kron4ek",
    "CachyOS/proton-cachyos": "proton-cachyos",
    "Castro-Fidel/wine_builds": "LG"
}

mirrors = {
    "https://cloud.linux-gaming.ru": "LG_mirror"
}

def source_list_checker():
    for repo, short_name in repos.items():
        output_file = os.path.join(tmp_path, f"{short_name}.tmp")

        if not os.path.exists(output_file) or os.path.getsize(output_file) == 0 or \
                (time.time() - get_last_modified_time(output_file, fallback=0)) >= 10800:
            source_list_downloader(repo, short_name, output_file)
        else:
            log.info(f"Файл {output_file} существует и был обновлён менее 3 часов назад. Используем кэшированные данные.")

    for mirror_url, short_name in mirrors.items():
        output_file = os.path.join(tmp_path, f"{short_name}.tmp")

        if not os.path.exists(output_file) or os.path.getsize(output_file) == 0 or \
                (time.time() - get_last_modified_time(output_file, fallback=0)) >= 10800:
            source_list_downloader(mirror_url, short_name, output_file, use_github=False)
        else:
            log.info(f"Файл {output_file} существует и был обновлён менее 3 часов назад. Используем кэшированные данные.")

def filter_asset(asset_name):
    filtered_assets = []

    if (
            (re.search(r'(wine|proton)', asset_name, re.IGNORECASE) or
             re.search(r'^GE-Proton\d+-\d+\.tar\.gz$', asset_name) or
             re.search(r'^GE-Proton\d+(-\d+)?\.tar\.xz$', asset_name)) and
            (asset_name.endswith('.tar.gz') or asset_name.endswith('.tar.xz'))
    ):
        if not (
                re.search(r'Proton-6\.5-GE-2', asset_name) or
                re.search(r'6\.23', asset_name) or
                re.search(r'"-x86.tar.xz"|"-wow64.tar.xz"', asset_name) or
                re.search(r'plugins', asset_name) or
                re.search(r'x86_64_v3', asset_name)
        ):
            filtered_assets.append(asset_name)

    log.debug(f"Отфильтрованный файл: {filtered_assets}")
    return filtered_assets

def source_list_downloader(source, short_name, output_file, use_github=True):
    if use_github:
        url = f"https://api.github.com/repos/{source}/releases"
    else:
        url = f"{source}/"

    temp_file = os.path.join(tmp_path, f"{short_name}.tmp.new")

    try:
        response = requests.get(url)
        response.raise_for_status()

        tar_urls = []

        if use_github:
            releases = response.json()
            for release in releases:
                assets = release.get('assets', [])
                for asset in assets:
                    asset_name = asset['name']
                    asset_url = asset['browser_download_url']
                    filtered_assets = filter_asset(asset_name)
                    if filtered_assets:
                        tar_urls.append(asset_url)
        else:
            content = response.text
            log.debug(f"Содержимое зеркала assets: {content}")

            relative_urls = re.findall(r'download=[\'"]?([^\'" >]+\.tar\.(gz|xz))[\'"]?', content)

            base_url = "https://cloud.linux-gaming.ru/portproton/"
            for url_tuple in relative_urls:
                asset_name = url_tuple[0]
                filtered_assets = filter_asset(asset_name)
                for filtered_asset in filtered_assets:
                    asset_url = base_url + filtered_asset
                    tar_urls.append(asset_url)

        if not tar_urls:
            log.warning(f"Нет подходящих файлов в {'GitHub' if use_github else 'зеркале'} {source}.")
            return

        with open(temp_file, 'w') as file:
            file.write("\n".join(tar_urls))

        os.replace(temp_file, output_file)
        log.info(f"Файл {output_file} успешно обновлен.")

    except requests.exceptions.RequestException as e:
        log.error(f"Ошибка при получении данных из {source}: {str(e)}")

def get_sources(args, flag=False, mirror=True):
    os.makedirs(tmp_path, exist_ok=True)
    source_list_checker()

    if not args:
        log.critical("Аргументы не предоставлены. Завершение работы.")
        return

    if args == ["list"] and flag == "wine":
        try:
            tmp_files = os.listdir(tmp_path)
            tmp_files = [f for f in tmp_files if f.endswith('.tmp')]

            dist_files = os.listdir(dist_path)

            content = []

            for tmp_file in tmp_files:
                file_path = os.path.join(tmp_path, tmp_file)
                with open(file_path, 'r') as file:
                    url_content = file.read()
                    for line in url_content.splitlines():
                        if ".tar" in line:
                            last_slash_index = line.rfind('/')
                            tar_index = line.rfind('.tar')
                            if last_slash_index != -1 and tar_index != -1 and last_slash_index < tar_index:
                                filename = line[last_slash_index + 1:tar_index]
                                content.append(filename)

            matched_files = []
            for filename in content:
                if filename in dist_files:
                    matched_files.append(f"\033[92m{filename} [Установлено]\033[0m")  # Зелёный цвет
                else:
                    matched_files.append(filename)

            log.info("Результаты:")
            for file in matched_files:
                log.info(file)

        except Exception as e:
            log.error(f"Ошибка при обработке файлов в {tmp_path}: {e}")

    else:
        for arg in args:
            target_dir_path = os.path.join(dist_path, arg)

            if not os.path.isdir(target_dir_path):
                get_url_list(arg, mirror)
                continue

            log.debug(f"Запрашиваемый каталог '{arg}' найден в '{dist_path}'. Проверяем его содержимое.")
            metadata = load_metadata(os.path.join(target_dir_path, "metadata.json"))

            if metadata:
                if not compare_directory_with_metadata(dist_path, metadata):
                    log.debug(f"Содержимое каталога '{arg}' в '{dist_path}' не соответствует метаданным.")
                    get_url_list(arg, mirror)
                    continue

                log.debug(f"Содержимое каталога '{arg}' в '{dist_path}' соответствует метаданным.")
                continue

            log.debug(f"Каталог '{arg}' в '{dist_path}' не содержит метаданных.")
            get_url_list(arg, mirror)


def get_url_list(arg, mirror):
    file_found = False
    repo_items = list(repos.items())
    last_index = len(repo_items) - 1

    for index, (repo, short_name) in enumerate(repo_items):
        log.debug(f"Ищем {arg} в {repo} с помощью файла {short_name}.tmp")

        if mirror and index == last_index and short_name == "LG":
            short_name = "LG_mirror"

        tmp_file_path = os.path.join(tmp_path, f"{short_name}.tmp")

        if os.path.exists(tmp_file_path):
            with open(tmp_file_path, 'r') as file:
                all_urls = file.read().splitlines()
                log.debug(f"Получили ссылки {all_urls}")

            for url in all_urls:
                if f"{arg}.tar." in os.path.basename(url):
                    log.debug(f"Совпадение для '{arg}' найдено в файле {tmp_file_path}")
                    log.debug(f"Начинаем загрузку файла с URL: {url}")
                    tmp_file = os.path.join(tmp_path, os.path.basename(url))
                    log.debug(f"Сформирован путь к файлу: {tmp_file}")

                    try:
                        log.debug(f"Загружаем из зеркала: {url}")
                        shasum_suffix = ".sha256sum" if short_name in ["LG", "LG_mirror"] else ".sha512sum"
                        shasum_url = url.replace('.tar.gz', shasum_suffix).replace('.tar.xz', shasum_suffix)
                        shasum = get_shasum(shasum_url)

                        if shasum:
                            log.debug(f"Получили строку с хэш-суммой: {shasum}")
                            shasum = shasum.split()[0]
                            log.debug(f"Получили хэш-сумму: {shasum}")

                        if try_download(url, tmp_file, shasum):
                            if unpack(tmp_file, dist_path):
                                try_remove_file(tmp_file)
                            file_found = True
                        break
                    except Exception as e:
                        log.error(f"Произошла ошибка при попытке загрузить файл: {e}")
                        break  # Здесь можно добавить break, если нужно выйти при ошибке загрузки

    if not file_found:
        log.critical(f"{arg} не найден в файле {tmp_file_path}. Завершение! Проверьте корректность переданного имени wine/proton.")

def get_shasum(url):
    try:
        response = requests.get(url)
        response.raise_for_status()

        # Возвращаем содержимое файла
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при получении файла: {e}")