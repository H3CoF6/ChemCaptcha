from abc import ABC, abstractmethod
from typing import Dict, Any, Type, ClassVar
from app.utils.logger import logger


class BaseCaptcha(ABC):
    _registry: Dict[str, Type['BaseCaptcha']] = {}

    slug: ClassVar[str]

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        if cls.__name__ == 'BaseCaptcha':
            return

        if not hasattr(cls, 'slug') or not isinstance(cls.slug, str):
            raise TypeError(f"Class {cls.__name__} must define a string attribute 'slug'")

        if cls.slug in cls._registry:
            raise ValueError(f"Captcha slug '{cls.slug}' already registered!")

        cls._registry[cls.slug] = cls
        logger.info(f"[Plugin Registered]: {cls.slug} -> {cls.__name__}")

    @classmethod
    def get_plugins(cls):
        return cls._registry

    @abstractmethod
    def get_table_schema(self) -> str:
        """返回建表 SQL 语句"""
        pass

    @abstractmethod
    def generate(self, mol_path: str) -> dict:
        """生成验证码逻辑"""
        pass

    @abstractmethod
    def verify(self, answer_data: dict, user_input: Any) -> bool:
        """验证逻辑"""
        pass