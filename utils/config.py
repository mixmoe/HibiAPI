import os
from pathlib import Path
from typing import Generic, Optional, Type, TypeVar

import confuse  # type:ignore
from pydantic import BaseModel

CONFIG_DIR = Path(".") / "configs"


_T = TypeVar("_T")


for file in os.listdir(CONFIG_DIR):
    path = CONFIG_DIR / file
    if not file.endswith(".default.yml"):
        continue
    new_path = CONFIG_DIR / file.replace(".default", "")
    if new_path.is_file():
        continue
    new_path.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")


class _TypeChecker(BaseModel, Generic[_T]):
    value: _T


class ConfigSubView(confuse.Subview):
    def get(self, template: Optional[Type[_T]] = None) -> _T:
        try:
            return super().get(template=template or confuse.REQUIRED)  # type:ignore
        except Exception:
            return _TypeChecker[template](value=super().get()).value  # type:ignore

    def as_str(self) -> str:
        return super().as_str()  # type:ignore

    def as_number(self) -> int:
        return super().as_number()  # type:ignore

    def as_bool(self) -> bool:
        return self.get(bool)  # type:ignore

    def as_path(self) -> Path:
        return super().as_path()  # type:ignore

    def as_dict(self) -> dict:
        return self.get(dict)  # type:ignore

    def as_iterable(self, serializer: Optional[Type[_T]] = None) -> _T:
        value = self.get(list)
        return value if serializer is None else serializer(value)  # type:ignore

    def __getitem__(self, key: str):
        return self.__class__(self, key)


class AppConfig(confuse.Configuration):
    def __init__(self, name: str, path: Path):
        self._config_path = path
        self._config = self._config_path / (name + ".yml")
        self._default = self._generate_default_name(self._config)
        super().__init__(name)

    def config_dir(self) -> str:
        Path(self._config_path).mkdir(exist_ok=True, parents=True)
        return str(self._config_path)

    @staticmethod
    def _generate_default_name(path: Path):
        filename, ext = path.name.rsplit(".", 1)
        return path.with_name(filename + ".default." + ext)

    def user_config_path(self) -> str:
        return str(self._config)

    def _add_default_source(self):
        if self._default is None:
            return
        assert self._default.is_file()
        data = confuse.load_yaml(self._default, loader=self.loader)
        self.add(confuse.ConfigSource(data, filename=str(self._default), default=True))

    def _add_user_source(self):
        if not Path(self._config).is_file():
            Path(self._config).write_bytes(self._default.read_bytes())
        data = confuse.load_yaml(self._config, loader=self.loader)
        self.add(confuse.ConfigSource(data, filename=str(self._config), default=True))

    def __getitem__(self, key: str) -> ConfigSubView:
        return ConfigSubView(self, key)


class GeneralConfig(AppConfig):
    def __init__(self, name: str, path: Optional[Path] = None):
        super().__init__(name, path or CONFIG_DIR)


class APIConfig(GeneralConfig):
    pass


Config = GeneralConfig("general")
