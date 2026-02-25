import json
import logging
from typing import Dict, Any, Optional

# 配置日志（全局只配置一次）
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def read_json_file(file_path: str) -> Dict[str, Any]:
    """安全读取JSON文件，包含异常处理"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        logging.error(f"JSON文件不存在: {file_path}")
        raise
    except json.JSONDecodeError:
        logging.error(f"JSON文件格式错误: {file_path}")
        raise


def get_url_by_type(submit_type: str) -> Optional[str]:
    """根据提交类型（case/bug）返回对应URL"""
    from constants import CASE_URL, BUG_URL
    url_map = {
        "case": CASE_URL,
        "bug": BUG_URL
    }
    url = url_map.get(submit_type)
    if not url:
        logging.warning(f"无效的提交类型: {submit_type}，仅支持case/bug")
    return url
