#!/usr/bin/env python3

from modules.log import *
from modules.env_var import *
from modules.files_worker import *
from modules.downloader import *

if __name__ == "__main__":
    log.debug("Привет мир!")
    log.info("Привет мир!")
    log.warning("Привет мир!")
    log.error("Привет мир!")
    log.critical("Привет мир!")