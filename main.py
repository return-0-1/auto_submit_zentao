import logging
from business_handler import BusinessHandler
from constants import DEFAULT_MODULE, DEFAULT_SUBMIT_TYPE, DEFAULT_STORY_ID_LIST, USERNAME, PASSWORD


def main():
    """程序主入口"""
    try:
        # 初始化业务处理器
        handler = BusinessHandler(USERNAME, PASSWORD)

        # 处理指定的JSON文件
        for story_id in DEFAULT_STORY_ID_LIST:
            handler.process_file(story_id, DEFAULT_SUBMIT_TYPE, DEFAULT_MODULE)

    except Exception as e:
        logging.error(f"程序执行失败: {e}")
        raise


if __name__ == "__main__":
    main()
