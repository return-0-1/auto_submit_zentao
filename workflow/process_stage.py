import logging
from config import DOWNLOAD_FOLDER, OUTPUT_BASE_FOLDER


class ProcessStage:
    """处理阶段：处理下载的需求文件（待开发）"""

    def execute(self):
        logging.info("开始执行处理阶段")
        logging.info(f"输入文件夹: {DOWNLOAD_FOLDER}")
        logging.info(f"输出文件夹: {OUTPUT_BASE_FOLDER}")
        
        # TODO: 实现需求文件处理逻辑
        # 例如：解析PPTX、提取文本、整理格式等
        logging.warning("处理阶段尚未实现，跳过此阶段")
