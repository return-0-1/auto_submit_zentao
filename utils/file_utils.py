import json
import logging
import re
from typing import Dict, Any, Optional
import win32api

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def read_txt_file(file_path: str) -> str:
    """读取txt文件内容"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        logging.error(f"文件不存在: {file_path}")
        return ""
    except Exception as e:
        logging.error(f"读取文件失败: {file_path}, 错误: {str(e)}")
        return ""


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
    from config import CASE_URL, BUG_URL
    url_map = {
        "case": CASE_URL,
        "bug": BUG_URL
    }
    url = url_map.get(submit_type)
    if not url:
        logging.warning(f"无效的提交类型: {submit_type}，仅支持case/bug")
    return url


def clean_filename(raw_filename):
    """
    清理文件名，移除括号中的文件大小信息和其他多余内容

    Args:
        raw_filename: 原始文件名，如 "FeatureOutrectangleTouchFeature_新加算法需求.docx (39.87K)"

    Returns:
        str: 清理后的文件名，如 "FeatureOutrectangleTouchFeature_新加算法需求.docx"
    """
    cleaned = re.sub(r'\s*\([^)]*\)\s*', '', raw_filename)

    if cleaned == raw_filename:
        cleaned = re.sub(r'\s*\d*\.?\d+[KMGTPE]?B?\s*$', '', raw_filename)

    if cleaned == raw_filename:
        cleaned = re.sub(r'\s+[\d\.]+\s*[KMGTP]?B?\s*$', '', raw_filename)

    if not cleaned.strip():
        cleaned = raw_filename

    return cleaned.strip()


def clean_filename_advanced(raw_filename):
    """
    高级文件名清理方法，处理更多情况
    """
    patterns = [
        r'\s*\(\d+\.\d+[KMGTP]?\)\s*',
        r'\s*\d+\.\d+[KMGTP]?\s*',
        r'\s*\(\d+[KMGTP]?\)\s*',
        r'\s*\d+[KMGTP]?\s*',
        r'\s*\[[^\]]*\]\s*',
        r'\s*【[^】]*】\s*',
    ]

    cleaned = raw_filename
    for pattern in patterns:
        cleaned = re.sub(pattern, '', cleaned)

    cleaned = cleaned.strip().strip('.')

    return cleaned if cleaned else raw_filename
