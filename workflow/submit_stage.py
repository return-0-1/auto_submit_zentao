import logging
from core import BusinessHandler
from config.constants import USERNAME, PASSWORD, DEFAULT_STORY_ID_LIST, DEFAULT_SUBMIT_TYPE, DEFAULT_MODULE


class SubmitStage:
    """提交阶段：将GPT生成的结果提交到禅道"""

    def execute(self, story_ids: list = None):
        logging.info("开始执行提交阶段")
        target_story_ids = story_ids or DEFAULT_STORY_ID_LIST
        handler = None
        try:
            handler = BusinessHandler(USERNAME, PASSWORD)
            
            for story_id in target_story_ids:
                logging.info(f"处理需求: {story_id}")
                handler.process_file(story_id, DEFAULT_SUBMIT_TYPE, DEFAULT_MODULE)
            
            logging.info("提交阶段执行完成")
        except Exception as e:
            logging.error(f"提交阶段执行失败: {e}")
            raise
        finally:
            if handler:
                handler.close()
