import uvicorn

from app import app as AppRoot
from utils.config import Config
from utils.log import LOG_LEVEL, logger

COPYRIGHT = r"""<g><b>
  _    _   _   _       _              _____    _____ 
 | |  | | (_) | |     (_)     /\     |  __ \  |_   _|
 | |__| |  _  | |__    _     /  \    | |__) |   | |  
 |  __  | | | | '_ \  | |   / /\ \   |  ___/    | |  
 | |  | | | | | |_) | | |  / ____ \  | |       _| |_ 
 |_|  |_| |_| |_.__/  |_| /_/    \_\ |_|      |_____|
</b></g>
An alternative implement of Imjad API"""  # noqa:W291,W293

if __name__ == "__main__":
    logger.warning(COPYRIGHT)
    uvicorn.run(
        AppRoot,
        host=Config["server"]["host"].as_str(),
        port=Config["server"]["port"].as_number(),
        debug=Config["debug"].as_bool(),
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
