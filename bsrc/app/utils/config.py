import os

# 路径配置
CURRENT_DIR = os.path.dirname(__file__)
MOL_DIR = os.path.join(CURRENT_DIR, "..", "..", "data", "mol")
DATABASE_DIR = os.path.join(CURRENT_DIR, "..", "..", "data", "db")
LOG_PATH = os.path.join(CURRENT_DIR, "..", "..", "data", "log")
MOL_DB_PATH = os.path.join(DATABASE_DIR, "mol.db")

# 日志等级
TERMINAL_LOG_LEVEL = "INFO"
FILE_LOG_LEVEL = "DEBUG"

# AES加解密  不需要环境变量，只是略微增加前端逆向难度
# 不要用这么蠢的密码！！
AES_KEY = "1234567890987654"
AES_IV = "9876543210123456"