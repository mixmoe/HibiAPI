import os
from pathlib import Path
from typing import Optional

import click
import uvicorn

from hibiapi import __file__ as root_file
from hibiapi import __version__
from hibiapi.utils.config import CONFIG_DIR, DEBUG, DEFAULT_DIR, Config
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

try:
    width, height = os.get_terminal_size()
except OSError:
    width, height = 0, 0


@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx: click.Context):
    if not ctx.invoked_subcommand:
        logger.warning(
            f"Directly usage of <y>{ctx.info_name}</y> is <b><r>deprecated</r></b>, "
            f"please use <g>{ctx.info_name} run</g> instead."
        )
        ctx.invoke(run)


@main.command(help="to run the server")
@click.option(
    "--host",
    "-h",
    default=Config["server"]["host"].as_str(),
    help="listened server address",
    show_default=True,
)
@click.option(
    "--port",
    "-p",
    default=Config["server"]["port"].as_number(),
    help="listened server port",
    show_default=True,
)
@click.option(
    "--workers",
    "-w",
    default=1,
    help="amount of server workers",
    show_default=True,
)
@click.option(
    "--reload",
    "-r",
    default=DEBUG,
    help="automatic reload while file changes",
    show_default=True,
    is_flag=True,
)
def run(host: str, port: int, workers: int, reload: bool):
    logger.warning(
        "\n".join(i.center(width) for i in COPYRIGHT.splitlines()),
    )
    logger.info(f"HibiAPI version: <g><b>{__version__}</b></g>")
    logger.info(
        "Server is running under <b>{}</b> mode!".format(
            "<r>debug</r>" if DEBUG else "<g>production</g>"
        )
    )
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


@main.command(help="to generate a config file folder")
@click.option(
    "--force",
    "-f",
    default=False,
    is_flag=True,
    help="force recreate config folder, will delete existing config folder",
)
def config(force: bool):
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
            click.echo(
                click.style(("Overwritten" if existed else "Created") + ": ", fg="blue")
                + click.style(str(config_path), fg="yellow")
            )
    if total_written > 0:
        click.echo(f"Config folder generated, {total_written=}")


if __name__ == "__main__":
    main()
