import json
import os
from pathlib import Path
from typing import Any, Dict, List, Type, TypeVar, overload

import confuse
import dotenv
from pydantic import parse_obj_as

from hibiapi import __file__ as root_file

CONFIG_DIR = Path(".") / "configs"
DEFAULT_DIR = Path(root_file).parent / "configs"

_T = TypeVar("_T")


class ConfigSubView(confuse.Subview):
    @overload
    def get(self) -> Any:
        ...

    @overload
    def get(self, template: Type[_T]) -> _T:
        ...

    def get(self, template: Type[_T] = Any) -> _T:
        return parse_obj_as(template, super().get())

    def as_str(self) -> str:
        return self.get(str)

    def as_str_seq(self, split: str = "\n") -> List[str]:
        return [
            stripped
            for line in self.as_str().strip().split(split)
            if (stripped := line.strip())
        ]

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
        self._config = CONFIG_DIR / (filename := f"{name}.yml")
        self._default = DEFAULT_DIR / filename
        super().__init__(name)
        self._add_env_source()

    def config_dir(self) -> str:
        return str(CONFIG_DIR)

    def user_config_path(self) -> str:
        return str(self._config)

    def _add_env_source(self):
        if dotenv.find_dotenv():
            dotenv.load_dotenv()
        config_name = f"{self._config_name.lower()}_"
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
