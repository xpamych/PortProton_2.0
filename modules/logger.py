import logging
import sys

class ColoredFormatter(logging.Formatter):
    COLORS = {  # ANSI escape sequences for colors
        'DEBUG': '\033[35m',    # Purple
        'INFO': '\033[36m',     # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[41m',  # Red background
    }
    RESET = '\033[0m'  # Reset to default color

    def format(self, record):
        color = self.COLORS.get(record.levelname, self.RESET)
        message = super().format(record)
        formatted_message = f"{color}{message}{self.RESET}"
        if record.levelname == 'CRITICAL':
            print(formatted_message)
            sys.exit(1)
        return formatted_message


log = logging.getLogger() # Настраиваем логирование
def set_logging_level(level_string="INFO"):
    levels = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }

    level = levels.get(level_string, logging.WARNING)  # Уровень по умолчанию
    if level == logging.WARNING:
        print(f"Неизвестный уровень логирования: {level_string}. Устанавливается уровень WARNING.")
    return level

handler = logging.StreamHandler()  # Создаем консольный обработчик
handler.setFormatter(ColoredFormatter('%(levelname)s: %(message)s'))

# TODO: добавить условие для управления переменой пути сохранения лога
log_file_path = 'portproton.log'  # Это может быть переменная, установленная пользователем
file_handler = logging.FileHandler(log_file_path, mode='w')  # Создаем файловый обработчик
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s: %(message)s'))

log.addHandler(file_handler)
log.addHandler(handler)
