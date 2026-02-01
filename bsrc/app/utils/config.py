import os

# 设置
NOISE_MODE = True  # 启用噪声模式
DEV_MOD = True   # 开发模式，demo路由的注册

# AES加解密  不需要环境变量，只是略微增加前端逆向难度
# 不要用这么蠢的密码！！
FRONT_AES_KEY = "1234567890987654"
TOKEN_AES_KEY = os.getenv("AES_KEY", os.urandom(16))

FONT_NAME = "ComicNeue-Bold.ttf" # 不启用则留空

# 默认验证码大小  （这里略大了）
DEFAULT_WIDTH = 800
DEFAULT_HEIGHT = 600

# 有效期  // 2 min
EXPIRED_TIME = 120

# 路径配置
CURRENT_DIR = os.path.dirname(__file__)
MOL_DIR = os.path.join(CURRENT_DIR, "..", "..", "data", "mol")
SDF_DIR = os.path.join(CURRENT_DIR, "..", "..", "data", "sdf")
DATABASE_DIR = os.path.join(CURRENT_DIR, "..", "..", "data", "db")
LOG_PATH = os.path.join(CURRENT_DIR, "..", "..", "data", "log")
MOL_DB_PATH = os.path.join(DATABASE_DIR, "mol.db")
FONT_DIR = os.path.join(CURRENT_DIR, "..", "..", "data", "fonts")

# 日志等级
TERMINAL_LOG_LEVEL = "INFO"
FILE_LOG_LEVEL = "DEBUG"

