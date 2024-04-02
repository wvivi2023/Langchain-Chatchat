import logging
import os
import langchain
import tempfile
import shutil
from logging.handlers import RotatingFileHandler

# 是否显示详细日志
log_verbose = False
langchain.verbose = False

# 通常情况下不需要更改以下内容

# 日志格式
LOG_FORMAT = "%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s"
logger = logging.getLogger()

LOG_BACKUP_COUNT = 10  # 保留的归档文件数量
LOG_MAX_FILE_SIZE = 1024 * 1024  # 每个日志文件的最大大小（以字节为单位）

# 创建日志记录器并设置日志级别
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

# 日志存储路径
LOG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
if not os.path.exists(LOG_PATH):
    os.mkdir(LOG_PATH)

# 临时文件目录，主要用于文件对话
BASE_TEMP_DIR = os.path.join(tempfile.gettempdir(), "chatchat")
try:
    shutil.rmtree(BASE_TEMP_DIR)
except Exception:
    pass
os.makedirs(BASE_TEMP_DIR, exist_ok=True)


# 创建文件处理程序，并设置日志级别和文件名
file_handler = RotatingFileHandler(LOG_PATH +'/app.log', maxBytes=LOG_MAX_FILE_SIZE, backupCount=LOG_BACKUP_COUNT)
file_handler.setLevel(logging.INFO)

# # 设置日志记录格式
formatter = logging.Formatter(LOG_FORMAT)
file_handler.setFormatter(formatter)

# 获取日志记录器并添加文件处理程序
logger.addHandler(file_handler)

