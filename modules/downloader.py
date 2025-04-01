import hashlib
import logging
import os

import requests

from tqdm import tqdm

from .logger import *
from .files_worker import *

def try_download(url, save_path=None, expected_hash=None):
    """
    Скачивает файл по 0указанному URL с отображением прогресса и проверкой хеш-суммы.

    :param url: URL файла для скачивания.
    :param expected_hash: Ожидаемая хеш-сумма SHA-512 для проверки.
    :param save_path: Путь для сохранения файла. Если None или директория, то используется имя файла из URL.
    """
    max_attempts = 3
    attempt = 0
    while attempt < max_attempts:
        try:
            if save_path:
                log.debug(f"Проверка наличия файла: {save_path}")
                if os.path.exists(save_path):  # Проверяем хеш существующего файла
                    existing_hash = check_hash_sum(save_path, expected_hash)
                    logging.debug(f"Проверка хеш-суммы файла {save_path} ожидаемая сумма: {expected_hash} и фактическая: {existing_hash}")
                    if existing_hash:
                        log.info(f"Файл уже скачан и хеш совпадает: {save_path}. Скачивание пропущено.")
                        return True
                    else:
                        file_size = os.path.getsize(save_path)
                        headers = {'Range': f'bytes={file_size}-'}  # Заголовок для докачки
                        log.info(f"Продолжаем скачивание файла с {file_size} байта.")
                else:
                    file_size = 0
                    headers = {}
            else:
                log.error("Путь для сохранения (save_path) не задан.")
                return False

            response = requests.get(url, headers=headers, stream=True)
            response.raise_for_status() # Проверка статуса ответа, если не 200, то выбрасывается исключение

            if save_path is None:
                save_path = os.path.join(tmp_path, os.path.basename(url))
            elif os.path.isdir(save_path):
                save_path = os.path.join(save_path, os.path.basename(url))

            if save_path is None or not save_path.strip():
                log.error("Не удалось сформировать корректный путь для сохранения файла.")
                return False

            total_size = int(response.headers.get("content-length", 0)) + file_size if 'content-length' in response.headers else None # Получаем общий размер файла (может не определяться при докачке)
            # TODO: резерв места
            with open(save_path, "ab") as file, tqdm(
                    desc=save_path,  # Описание для прогресс-бара
                    total=total_size,  # Общий размер файла
                    initial=file_size,  # Начальный размер для прогресс-бара
                    unit="B",  # Единица измерения (байты)
                    unit_scale=True,  # Масштабирование единиц (KB, MB и т.д.)
                    unit_divisor=1024,  # Делитель для масштабирования (1024 для KB, MB)
            ) as progress_bar:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
                    progress_bar.update(len(chunk))  # Обновляем прогресс-бар

            log.info(f"Файл успешно скачан и сохранён как {save_path}.")
            return True

        except requests.exceptions.RequestException as e:
            log.error(f"Ошибка при скачивании файла: {e}")
        except Exception as e:
            log.error(f"Неизвестная ошибка: {e}")
        except KeyboardInterrupt as e:
            log.critical(f"Прервано пользователем: {e}")
        return False