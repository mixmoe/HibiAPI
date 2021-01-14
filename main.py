from os import get_terminal_size

import uvicorn  # type:ignore

from app import app as AppRoot
from utils.config import DEBUG, VERSION, Config
from utils.log import LOG_LEVEL, logger

COPYRIGHT = r"""<b><g>
  _    _ _ _     _          _____ _____ 
 | |  | (_) |   (_)   /\   |  __ \_   _|
 | |__| |_| |__  _   /  \  | |__) || |  
 |  __  | | '_ \| | / /\ \ |  ___/ | |  
 | |  | | | |_) | |/ ____ \| |    _| |_ 
 |_|  |_|_|_.__/|_/_/    \_\_|   |_____|
</g><e>
An alternative implement of Imjad API
Project: https://github.com/mixmoe/HibiAPI
</e></b>"""  # noqa:W291,W293

try:
    width, height = get_terminal_size()
except OSError:
    width, height = 0, 0


if __name__ == "__main__":
    logger.warning("\n".join(i.center(width) for i in COPYRIGHT.splitlines()))
    logger.info("HibiAPI version: <g><b>%s</b></g>" % VERSION)
    logger.info(
        "Server is running under <b>%s</b> mode!"
        % ("<r>debug</r>" if DEBUG else "<g>production</g>")
    )
    uvicorn.run(
        AppRoot,
        host=Config["server"]["host"].as_str(),
        port=Config["server"]["port"].as_number(),
        debug=DEBUG,
        access_log=False,
        log_config={
            "version": 1,
            "disable_existing_loggers": False,
            "handlers": {
                "default": {
                    "class": "utils.log.LoguruHandler",
                },
            },
            "loggers": {
                "uvicorn.error": {
                    "handlers": ["default"],
                    "level": LOG_LEVEL,
                },
                "uvicorn.access": {
                    "handlers": ["default"],
                    "level": LOG_LEVEL,
                },
            },
        },
    )
