# 常量定义

# 尝试从环境变量读取配置
import os

# 支持通过 .env 文件加载环境变量
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # 如果没有安装 python-dotenv，直接使用环境变量

# ============ 安全配置（从环境变量读取） ============

# 禅道登录配置
USERNAME = os.environ.get('ZENTAO_USERNAME')
PASSWORD = os.environ.get('ZENTAO_PASSWORD')

# GPT API 配置
GPT_API_KEY = os.environ.get('GPT_API_KEY')

# ============ 基础配置 ============

# GPT 配置
# GPT_PROVIDER: 可选值 "deepseek" 或 "qwen"，用于切换不同的GPT服务
GPT_PROVIDER = os.environ.get('GPT_PROVIDER', "deepseek")

# DeepSeek GPT 配置
DEEPSEEK_MODEL = "deepseek-chat"
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# Qwen GPT 配置（新接口）
QWEN_MODEL = os.environ.get('QWEN_MODEL', "Qwen3-14B")
QWEN_API_URL = os.environ.get('QWEN_API_URL', "http://192.168.7.70:5001/v1/chat-messages")
QWEN_API_KEY = os.environ.get('QWEN_API_KEY', "app-A1GY6j4iQCClkS7PNwCqAsq4")
QWEN_USER = os.environ.get('QWEN_USER', "tester1")

GPT_PROMPT_FILE = "prompt.txt"

# 调试模式配置
DEBUG_MODE = True  # 设为 True 时，表单提交操作将仅输出日志，不真正提交

# URL 配置
ZENTAO_BASE_URL = "http://192.168.7.3:82"  # 禅道服务器基础地址（用于API提交）
CASE_URL = "http://192.168.7.3:82/index.php?m=testcase&f=create&productID=4&branch=0&moduleID=0"
BUG_URL = "http://vxian.synology.me:82/index.php?m=bug&f=create&productID=33&branch=0&extra=moduleID=0"

# 路径配置（支持环境变量覆盖）
DRIVER_PATH = os.environ.get('DRIVER_PATH', "C:\\Users\\V072\\.wdm\\drivers\\edgedriver\\win64\\msedgedriver.exe")
NEED_URL = "http://192.168.7.3:82/index.php?m=story&f=view&t=html&id="
DOWNLOAD_FOLDER = os.environ.get('DOWNLOAD_FOLDER', "D:\\VayoPro\\需求方案\\down")
OUTPUT_BASE_FOLDER = os.environ.get('OUTPUT_BASE_FOLDER', "D:\\VayoPro\\需求方案\\mid")
JSON_DATA_PATH = os.environ.get('JSON_DATA_PATH', "D:\\VayoPro\\需求方案\\gpt_output\\")

# 默认配置
DEFAULT_MODULE = "/"
DEFAULT_SUBMIT_TYPE = "case"
DEFAULT_STORY_ID_LIST = [
    "3795",
    "3781",
    "3820"
]

# 产品ID
PRODUCT_DICT = {
    "Vayo SWS 软件V1": 74,
    "Vayo Jetting软件V1": 73,
    "vSDK": 71,
    "DFX MetaLab": 70,
    "Vayo Stencil": 68,
    "V-Accelerator": 67,
    "DFXgo": 66,
    "Vayo Gerber": 65,
    "Vayo Test V6": 64,
    "Vayo ServiceManager V5": 63,
    "XC/Vayo-SMT": 61,
    "Vayo DFA": 50,
    "Vayo-Panel": 34,
    "Vayo-CAM365R": 33,
    "Vayo-Dispensing Accelerator": 30,
    "Vayo-View": 22,
    "Vayo-AOI&AXI Accelerator": 18,
    "Vayo-CAM365": 17,
    "Vayo-AutoFeederlist": 16,
    "Vayo-Gerber View": 15,
    "Component Library Manager": 11,
    "VayoPro-SPI Expert": 10,
    "VayoPro-View Expert ": 9,
    "VayoPro-Gerber": 8,
    "VayoPro-ServiceManager": 7,
    "VayoPro-Document Expert": 6,
    "VayoPro-Test Expert": 5,
    "Vayo-Stencil Designer": 4,
    "VayoPro-SMT Expert": 3,
    "VayoPro-DFM Expert": 1,
    "Vayo AI数字工艺软件": 72,
    "PCBA装联编程软件V2": 69,
    "望友客户拜访服务查询系统": 60,
    "PCBA装联编程": 56,
    "Vayo-FAI Meta": 35,
    "SO出货管理系统": 32,
    "Vayo-PCA数字化工艺设计平台": 31,
    "电缆网工艺审查系统": 25,
    "Vayo业务报备管理系统": 21,
    "Vayo-DFX设计执行系统": 20,
    "Vayo-SMT Meta": 19,
    "VayoPro-CAD Converter": 53,
    "Vayo-ASM": 27,
    "Vayo-Cutting Accelerator": 57,
    "Vayo-SolderPaste Converter": 55,
    "外部项目产品模块汇总": 49,
    "VayoPro License Statistics": 29,
    "Vayo-DFX设计执行系统（教育版）": 62,
    "可制造性审查软件 Vayo DFM V8 (Plus)": 58,
    "Vayo翻译": 51,
    "Vayo-SPI Accelerator": 2
}