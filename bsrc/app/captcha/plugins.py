"""
自动扫描 app/captcha 下的所有子包，并进行 import。
这会触发 BaseCaptcha.__init_subclass__ 完成注册。
"""

import pkgutil
import importlib
import os
import app.captcha
from app.captcha.base import BaseCaptcha
from app.utils.logger import logger


def load_all_plugins():
    package_path = os.path.dirname(app.captcha.__file__)

    for _, name, is_pkg in pkgutil.iter_modules([package_path]):
        if is_pkg:
            try:
                module_name = f"app.captcha.{name}.object"
                importlib.import_module(module_name)
            except ImportError:
                logger.error(f"plugin {name} import error!!")


load_all_plugins()
PLUGINS = BaseCaptcha.get_plugins()
