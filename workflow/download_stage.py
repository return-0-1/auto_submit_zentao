import logging
from core import BusinessHandler
from config.constants import USERNAME, PASSWORD, DOWNLOAD_FOLDER, DEFAULT_STORY_ID_LIST


class DownloadStage:
    """下载阶段：从禅道下载需求文件"""

    def execute(self, story_ids: list = None):
        logging.info("开始执行下载阶段")
        target_story_ids = story_ids or DEFAULT_STORY_ID_LIST
        try:
            handler = BusinessHandler(USERNAME, PASSWORD)
            handler.download_story_files(target_story_ids, DOWNLOAD_FOLDER)
            logging.info(f"文件已下载到: {DOWNLOAD_FOLDER}")
        except Exception as e:
            logging.error(f"下载阶段执行失败: {e}")
            raise
