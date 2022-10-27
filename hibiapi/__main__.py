import os
from pathlib import Path
from typing import Optional

import typer
import uvicorn

from hibiapi import __file__ as root_file
from hibiapi import __version__
from hibiapi.utils.config import CONFIG_DIR, DEFAULT_DIR, Config
from hibiapi.utils.log import LOG_LEVEL, logger

COPYRIGHT = r"""
<b><g>
  _    _ _ _     _          _____ _____  
 | |  | (_) |   (_)   /\   |  __ \_   _| 
 | |__| |_| |__  _   /  \  | |__) || |   
 |  __  | | '_ \| | / /\ \ |  ___/ | |   
 | |  | | | |_) | |/ ____ \| |    _| |_  
 |_|  |_|_|_.__/|_/_/    \_\_|   |_____| 
</g><e>
A program that implements easy-to-use APIs for a variety of commonly used sites
Repository: https://github.com/mixmoe/HibiAPI
</e></b>""".strip()  # noqa:W291


LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "default": {
            "class": "hibiapi.utils.log.LoguruHandler",
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
}


cli = typer.Typer()


@cli.callback(invoke_without_command=True)
@cli.command()
def run(
    ctx: typer.Context,
    host: str = Config["server"]["host"].as_str(),
    port: int = Config["server"]["port"].as_number(),
    workers: int = 1,
    reload: bool = False,
):
    if ctx.invoked_subcommand is None:
        logger.warning(
            f"Directly usage of command <r>{ctx.info_name}</r> is <b>deprecated</b>, "
            f"please use <g>{ctx.info_name} run</g> instead."
        )
    else:
        return

    try:
        terminal_width, _ = os.get_terminal_size()
    except OSError:
        terminal_width = 0
    logger.warning(
        "\n".join(i.center(terminal_width) for i in COPYRIGHT.splitlines()),
    )
    logger.info(f"HibiAPI version: <g><b>{__version__}</b></g>")

    uvicorn.run(
        "hibiapi.app:app",
        host=host,
        port=port,
        access_log=False,
        log_config=LOG_CONFIG,
        workers=workers,
        reload=reload,
        reload_dirs=[
            *map(str, [Path(root_file).parent.absolute(), CONFIG_DIR.absolute()])
        ],
        reload_includes=["*.py", "*.yml"],
        forwarded_allow_ips=Config["server"]["allowed-forward"].get(Optional[str]),
    )


@cli.command()
def config(force: bool = False):
    total_written = 0
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    for file in os.listdir(DEFAULT_DIR):
        default_path = DEFAULT_DIR / file
        config_path = CONFIG_DIR / file
        if not (existed := config_path.is_file()) or force:
            total_written += config_path.write_text(
                default_path.read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            typer.echo(
                typer.style(("Overwritten" if existed else "Created") + ": ", fg="blue")
                + typer.style(str(config_path), fg="yellow")
            )
    if total_written > 0:
        typer.echo(f"Config folder generated, {total_written=}")


if __name__ == "__main__":
    cli()
