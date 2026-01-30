from abc import ABC, abstractmethod
from typing import Dict, Any, Type, ClassVar, Optional
from app.utils.logger import logger
from rdkit import Chem
from app.utils.exceptions import PluginException


class BaseCaptcha(ABC):
    _registry: Dict[str, Type['BaseCaptcha']] = {}

    slug: ClassVar[str]
    table_name: ClassVar[str] # sqlite中的表名！！

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        if cls.__name__ == 'BaseCaptcha':
            return

        if not hasattr(cls, 'slug') or not isinstance(cls.slug, str):
            raise PluginException(f"Class {cls.__name__} must define a string attribute 'slug'")

        if not hasattr(cls, 'table_name') or not isinstance(cls.table_name, str):
            raise PluginException(f"Class {cls.__name__} must define a string attribute 'table_name'")

        if cls.slug in cls._registry:
            raise PluginException(f"Captcha slug '{cls.slug}' already registered!")

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
    def generate_img(self) -> dict:
        """
        生成验证码
        :return: {
            "img_base64": "...",
            "size": { ... }
        }
        """
        pass

    @abstractmethod
    def generate_answer(self) -> list:
        """
        生成答案
        :return: list[答案]
        """
        pass

    @abstractmethod
    def generate_read_output(self) -> str:
        """
        生成人类可读的题目文字描述
        :return: str 描述
        """
        pass


    @abstractmethod
    def verify(self, answer_data: dict, user_input: Any) -> bool:
        """验证逻辑"""
        pass


    @abstractmethod
    def get_metadata(self, mol: Chem.Mol) -> Optional[Dict[str, Any]]:
        """
        :param mol: RDKit 分子对象
        :return: 一个字典，包含该插件特有的字段数据。如果返回 None，表示该分子不符合入库要求。

        例子: 芳香环插件返回 -> {"has_aromatic": True, "ring_count": 3}
              手性碳插件返回 -> {"chiral_count": 2}
        """
        pass



class BaseOptions(ABC):
    """
    验证码插件的选项，例如：点击所有可能的（非醛基的）氢键供体
    """
    _registry: Dict[str, Type['BaseOptions']] = {}
    slug: ClassVar[str]

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        if cls.__name__ == 'BaseOptions':
            return

        if not hasattr(cls, 'slug') or not isinstance(cls.slug, str):
            raise PluginException(f"Class {cls.__name__} must define a string attribute 'slug'")

        if cls.slug in cls._registry:
            raise PluginException(f"Options slug '{cls.slug}' already registered!")

        cls._registry[cls.slug] = cls
        logger.info(f"[Plugin Options Registered]: {cls.slug} -> {cls.__name__}")

    @classmethod
    def get_plugins_options(cls):
        return cls._registry


    @abstractmethod
    def get_random_options(self):
        """
        获取随机的选项
        """
        pass

    @abstractmethod
    def check_all_options(self):
        """
        检查全部的可用选项
        """
        pass

    @abstractmethod
    def get_options(self):
        """
        获取当前的选项配置
        """
        pass

