import logging
from core import BusinessHandler
from config.constants import USERNAME, PASSWORD, DOWNLOAD_FOLDER, DEFAULT_STORY_ID_LIST


class DownloadStage:
    """下载阶段：从禅道下载需求文件"""

    def execute(self, story_ids: list = None, handler: BusinessHandler = None):
        logging.info("开始执行下载阶段")
        target_story_ids = story_ids or DEFAULT_STORY_ID_LIST
        
        # 使用传入的handler或创建新的handler（保持向后兼容）
        use_existing_handler = handler is not None
        current_handler = handler if handler else BusinessHandler(USERNAME, PASSWORD)
        
        try:
            current_handler.download_story_files(target_story_ids, DOWNLOAD_FOLDER)
            logging.info(f"文件已下载到: {DOWNLOAD_FOLDER}")
        except Exception as e:
            logging.error(f"下载阶段执行失败: {e}")
            raise
        finally:
            # 如果是新创建的handler，需要关闭；如果是传入的handler，由调用方负责关闭
            if not use_existing_handler and current_handler:
                current_handler.close()
