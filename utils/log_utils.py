import logging
import os
from datetime import datetime, timedelta
from logging.handlers import TimedRotatingFileHandler
from typing import Optional


class LogConfig:
    """日志配置类"""
    
    def __init__(self):
        self.log_level = logging.INFO
        self.log_dir = "logs"
        self.log_file_prefix = "zentao_auto"
        self.keep_days = 7
        self.console_enabled = True
        self.file_enabled = True


def setup_logging(
    log_level: int = logging.INFO,
    log_dir: str = "logs",
    log_file_prefix: str = "zentao_auto",
    keep_days: int = 7,
    console_enabled: bool = True,
    file_enabled: bool = True
) -> None:
    """
    配置日志系统
    
    Args:
        log_level: 日志级别，默认 INFO
        log_dir: 日志文件存放目录，默认 logs
        log_file_prefix: 日志文件前缀，默认 zentao_auto
        keep_days: 日志保留天数，默认 7 天
        console_enabled: 是否输出到控制台，默认 True
        file_enabled: 是否输出到文件，默认 True
    """
    # 创建日志目录
    if file_enabled and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 创建根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # 清除已存在的处理器（避免重复添加）
    root_logger.handlers = []
    
    # 日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 控制台处理器
    if console_enabled:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # 文件处理器（按日期分割）
    if file_enabled:
        log_file_path = os.path.join(log_dir, f"{log_file_prefix}.log")
        
        # TimedRotatingFileHandler 按日期分割
        file_handler = TimedRotatingFileHandler(
            log_file_path,
            when='midnight',      # 每天午夜分割
            interval=1,           # 间隔1天
            backupCount=keep_days, # 保留天数
            encoding='utf-8'
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    logging.info(f"日志系统初始化完成，级别: {logging.getLevelName(log_level)}")
    if file_enabled:
        logging.info(f"日志文件目录: {os.path.abspath(log_dir)}")
        logging.info(f"日志保留天数: {keep_days} 天")


def get_logger(name: str = None) -> logging.Logger:
    """
    获取日志记录器
    
    Args:
        name: 日志记录器名称，默认为 None（返回根日志记录器）
    
    Returns:
        日志记录器实例
    """
    return logging.getLogger(name)


def cleanup_old_logs(log_dir: str = "logs", keep_days: int = 7) -> None:
    """
    清理过期日志文件
    
    Args:
        log_dir: 日志目录
        keep_days: 保留天数
    """
    if not os.path.exists(log_dir):
        return
    
    cutoff_time = datetime.now() - timedelta(days=keep_days)
    
    for filename in os.listdir(log_dir):
        if filename.startswith("zentao_auto") and filename.endswith(".log"):
            filepath = os.path.join(log_dir, filename)
            try:
                file_mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                if file_mtime < cutoff_time:
                    os.remove(filepath)
                    logging.info(f"已清理过期日志文件: {filename}")
            except Exception as e:
                logging.error(f"清理日志文件失败 {filename}: {e}")


def log_level_from_string(level_str: str) -> int:
    """
    从字符串转换为日志级别
    
    Args:
        level_str: 日志级别字符串（DEBUG, INFO, WARNING, ERROR, CRITICAL）
    
    Returns:
        对应的日志级别整数
    """
    level_map = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    return level_map.get(level_str.upper(), logging.INFO)