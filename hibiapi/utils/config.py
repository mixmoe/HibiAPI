import json
import os
from pathlib import Path
from typing import Any, Dict, List, Type, TypeVar, overload

import confuse  # type:ignore
import dotenv
from pydantic import parse_obj_as

from hibiapi import __file__ as root_file

CONFIG_DIR = Path(".") / "configs"
DEFAULT_DIR = Path(root_file).parent / "configs"

_T = TypeVar("_T")


def _generate_default() -> int:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    generated = 0
    for file in os.listdir(DEFAULT_DIR):
        default_path = DEFAULT_DIR / file
        config_path = CONFIG_DIR / file
        if config_path.is_file():
            continue
        generated += config_path.write_text(
            default_path.read_text(encoding="utf-8"),
            encoding="utf-8",
        )
    return generated


if dotenv.find_dotenv():
    assert dotenv.load_dotenv(), "Failed to load .env"
else:
    assert _generate_default() <= 0, "Please complete config file!"


class ConfigSubView(confuse.Subview):
    @overload
    def get(self) -> Any:
        ...

    @overload
    def get(self, template: Type[_T]) -> _T:
        ...

    def get(self, template: Type[_T] = Any) -> _T:  # type: ignore
        return parse_obj_as(template, super().get())

    def as_str(self) -> str:
        return self.get(str)

    def as_str_seq(self, split: str = "\n") -> List[str]:
        return self.as_str().strip().split(split)

    def as_number(self) -> int:
        return self.get(int)

    def as_bool(self) -> bool:
        return self.get(bool)

    def as_path(self) -> Path:
        return self.get(Path)

    def as_dict(self) -> Dict[str, Any]:
        return self.get(Dict[str, Any])

    def __getitem__(self, key: str) -> "ConfigSubView":
        return self.__class__(self, key)


class AppConfig(confuse.Configuration):
    def __init__(self, name: str):
        self._config_name = name
        self._config = CONFIG_DIR / (filename := name + ".yml")
        self._default = DEFAULT_DIR / filename
        super().__init__(name)
        self._add_env_source()

    def config_dir(self) -> str:
        return str(CONFIG_DIR)

    def user_config_path(self) -> str:
        return str(self._config)

    def _add_env_source(self):
        config_name = self._config_name.lower() + "_"
        env_configs = {
            k[len(config_name) :].lower(): str(v)
            for k, v in os.environ.items()
            if k.lower().startswith(config_name)
        }
        # Convert `AAA_BBB_CCC=DDD` to `{'aaa':{'bbb':{'ccc':'ddd'}}}`
        source_tree: Dict[str, Any] = {}
        for key, value in env_configs.items():
            _tmp = source_tree
            *nodes, name = key.split("_")
            for node in nodes:
                _tmp = _tmp.setdefault(node, {})
            if value == "":
                continue
            try:
                _tmp[name] = json.loads(value)
            except json.JSONDecodeError:
                _tmp[name] = value

        self.sources.insert(0, confuse.ConfigSource.of(source_tree))

    def _add_default_source(self):
        self.add(confuse.YamlSource(self._default, default=True))

    def _add_user_source(self):
        self.add(confuse.YamlSource(self._config, optional=True))

    def __getitem__(self, key: str) -> ConfigSubView:
        return ConfigSubView(self, key)


class GeneralConfig(AppConfig):
    def __init__(self, name: str):
        super().__init__(name)


class APIConfig(GeneralConfig):
    pass


Config = GeneralConfig("general")

DATA_PATH = Config["data"]["path"].as_path().expanduser().absolute()
DEBUG = Config["debug"].as_bool()
