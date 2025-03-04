import logging
import sys

class ColoredFormatter(logging.Formatter):
    # ANSI escape sequences for colors
    COLORS = {
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

# Настраиваем логирование
log = logging.getLogger()
# TODO: добавить case с переменной для управление уровнем
log.setLevel(logging.DEBUG)

# Создаем консольный обработчик
handler = logging.StreamHandler()
handler.setFormatter(ColoredFormatter('%(levelname)s: %(message)s'))

# Создаем файловый обработчик
# TODO: добавить условие для управления перемееной пути сохранения лога
file_handler = logging.FileHandler('app.log')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s: %(message)s'))
log.addHandler(file_handler)

log.addHandler(handler)
