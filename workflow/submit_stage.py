import logging
from core import BusinessHandler
from config.constants import USERNAME, PASSWORD, DEFAULT_STORY_ID_LIST, DEFAULT_SUBMIT_TYPE, DEFAULT_MODULE


class SubmitStage:
    """提交阶段：将GPT生成的结果提交到禅道"""

    def execute(self, story_ids: list = None, handler: BusinessHandler = None):
        logging.info("开始执行提交阶段")
        target_story_ids = story_ids or DEFAULT_STORY_ID_LIST
        
        # 使用传入的handler或创建新的handler（保持向后兼容）
        use_existing_handler = handler is not None
        current_handler = handler if handler else BusinessHandler(USERNAME, PASSWORD)
        
        try:
            for story_id in target_story_ids:
                logging.info(f"处理需求: {story_id}")
                current_handler.process_file(story_id, DEFAULT_SUBMIT_TYPE, DEFAULT_MODULE)
            
            logging.info("提交阶段执行完成")
        except Exception as e:
            logging.error(f"提交阶段执行失败: {e}")
            raise
        finally:
            # 如果是新创建的handler，需要关闭；如果是传入的handler，由调用方负责关闭
            if not use_existing_handler and current_handler:
                current_handler.close()
