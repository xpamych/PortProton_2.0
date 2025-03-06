import json
from .log import *
from .env_var import *

def var(var_name):
    py_work_path = get_env_var("PYTHON_WORK_PATH")

    # Читаем конфигурационный файл
    with open(py_work_path + "/config.json", "r") as file:
        config = json.load(file)
    if config[var_name]:
        return config[var_name]
    else:
        log.critical(f"в config.json нет значения переменной: {var_name}")
