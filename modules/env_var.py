import os
from .log import *

# функции обработки переменных LINUX окружения
def print_env_var(var_name):
    if var_name in os.environ:
        value = os.environ[var_name]
        log.info(f"Переменная {var_name}={value}")
    else:
        log.warning(f"Переменная {var_name} не определена")

def check_and_set_env_var(var_name, default_value):
    if var_name not in os.environ or not os.environ[var_name]:
        os.environ[var_name] = default_value

def add_to_env_var(var_name, separator, value):
    if var_name not in os.environ:
        os.environ[var_name] = value
    else:
        current_value = os.environ.get(var_name)
        s = separator
        if s + value + s not in s + current_value + s:
            new_value = f"{current_value}{separator}{value}"
            os.environ[var_name] = new_value

def rm_from_env_var(var_name, separator, value):
    current_value = os.environ.get(var_name)
    if value in current_value.split(separator):
        new_value = separator.join([v for v in current_value.split(separator) if v != value])
        os.environ[var_name] = new_value

def env_var(var_name, value):
    match var_name:
        case "WINEDLLOVERRIDES":
            add_to_env_var("WINEDLLOVERRIDES", ";", value)
        case "VKD3D_CONFIG":
            add_to_env_var("VKD3D_CONFIG", ";", value)
        case "RADV_PERFTEST":
            add_to_env_var("RADV_PERFTEST", ";", value)
        case "PW_VK_INSTANCE_LAYERS":
            add_to_env_var("PW_VK_INSTANCE_LAYERS", ":", value)
        case "LD_LIBRARY_PATH":
            add_to_env_var("LD_LIBRARY_PATH", ":", value)
