import os

CURRENT_DIR = os.path.dirname(__file__)
MOL_DIR = os.path.join(CURRENT_DIR, "..", 'mol')

REDIS_URL = 'redis://localhost:6379/0'