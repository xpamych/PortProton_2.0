import os
from .logger import *

# функции обработки переменных LINUX окружения
def print_env_var(*var_name):
    for v in var_name:
        if v in os.environ:
            value = os.environ[v]
            log.info(f"Переменная {v}={value}")
        else:
            log.warning(f"Переменная {v} не определена")

def set_env_var_if_none(var_name, default_value):
    if var_name not in os.environ or not os.environ[var_name]:
        os.environ[var_name] = default_value

def set_env_var_force(var_name, value):
    os.environ[var_name] = value

def get_env_var(var_name):
    if var_name in os.environ and os.environ[var_name]:
        return os.environ[var_name]
    elif var_name == "DEBUG":
        ...
    else:
        log.critical(f"Переменная {var_name} не определена")

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
        case "WINEDLLPATH":
            add_to_env_var("WINEDLLPATH", ":", value)
        case "VKD3D_CONFIG":
            add_to_env_var("VKD3D_CONFIG", ";", value)
        case "RADV_PERFTEST":
            add_to_env_var("RADV_PERFTEST", ";", value)
        case "VK_INSTANCE_LAYERS":
            add_to_env_var("VK_INSTANCE_LAYERS", ":", value)
        case "LD_LIBRARY_PATH":
            add_to_env_var("LD_LIBRARY_PATH", ":", value)
        case "PATH":
            add_to_env_var("PATH", ":", value)
