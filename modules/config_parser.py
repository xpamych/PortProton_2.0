import json
from .logger import *
from .env_var import *

def var(var_name):
    py_work_path = get_env_var("PYTHON_WORK_PATH")

    # Читаем конфигурационный файл
    try:
        with open(py_work_path + "/config.json", "r") as file:
            config = json.load(file)
            return config[var_name]
    except Exception as e:
        log.critical(f"в config.json нет значения переменной: {e}")
