import os

# 路径配置
CURRENT_DIR = os.path.dirname(__file__)
MOL_DIR = os.path.join(CURRENT_DIR, "..", "..", "data", "mol")
DATABASE_DIR = os.path.join(CURRENT_DIR, "..", "..", "data", "db")
LOG_PATH = os.path.join(CURRENT_DIR, "..", "..", "data", "log")

# 日志等级
TERMINAL_LOG_LEVEL = "INFO"
FILE_LOG_LEVEL = "DEBUG"