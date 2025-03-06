from .log import *
from .files_worker import *
from .config_parser import *

def init_wine(dist_path):
    used_wine_upper = var("used_wine").upper()

    if used_wine_upper != "SYSTEM":
        if used_wine_upper == "WINE_LG":
            used_wine = var("default_wine")
        elif used_wine_upper == "PROTON_LG":
            used_wine = var("default_proton")

        log.info(f"used wine: {used_wine}")
        wine_path = dist_path + "/" + used_wine
        log.info(wine_path)
        
    else:
        # TODO: добавить системный вайн
        ...
