import os
import requests
from tqdm import tqdm
from .log import *
from .files_worker import *

def try_download(url, save_path=None):
    """
    Скачивает файл по указанному URL с отображением прогресса.

    :param url: URL файла для скачивания.
    :param save_path: Путь для сохранения файла. Если None или директория, то используется имя файла из URL.
    """
    try:
        # Отправляем GET-запрос на скачивание файла
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Проверяем, что запрос успешен

        # Определяем имя файла, если save_path не указан
        if save_path is None:
            save_path = os.path.basename(url)
        elif os.path.isdir(save_path):
            save_path = save_path + "/" + os.path.basename(url)

        # Получаем общий размер файла
        total_size = int(response.headers.get("content-length", 0))

        # Открываем файл для записи в бинарном режиме
        with open(save_path, "wb") as file, tqdm(
            desc=save_path,  # Описание для прогресс-бара
            total=total_size,  # Общий размер файла
            unit="B",  # Единица измерения (байты)
            unit_scale=True,  # Масштабирование единиц (KB, MB и т.д.)
            unit_divisor=1024,  # Делитель для масштабирования (1024 для KB, MB)
        ) as progress_bar:
            # Читаем данные по частям и записываем в файл
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
                progress_bar.update(len(chunk))  # Обновляем прогресс-бар

        log.info(f"Файл успешно скачан и сохранён как {save_path}.")
    except requests.exceptions.RequestException as e:
        log.error(f"Ошибка при скачивании файла: {e}")
    except Exception as e:
        log.error(f"Неизвестная ошибка: {e}")
    except KeyboardInterrupt as e:
        log.error(f"Прервано пользователем: {e}")
