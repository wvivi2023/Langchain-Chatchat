import logging
import os
import langchain
import tempfile
import shutil


# 是否显示详细日志
log_verbose = False
langchain.verbose = False

# 通常情况下不需要更改以下内容

# 日志格式
LOG_FORMAT = "%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s"
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(format=LOG_FORMAT)


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


#added by weiweiwang for log

# 创建日志记录器并设置日志级别
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

# 创建文件处理程序，并设置日志级别和文件名
#appLogPath =  os.path.join(LOG_PATH, "app.log")
file_handler = logging.FileHandler(LOG_PATH +'/app.log')
file_handler.setLevel(logging.INFO)

# 设置日志记录格式
formatter = logging.Formatter(LOG_FORMAT)
file_handler.setFormatter(formatter)

# 获取日志记录器并添加文件处理程序
appLogger = logging.getLogger(__name__)
appLogger.addHandler(file_handler)