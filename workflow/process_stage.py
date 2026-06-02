import logging
from config.constants import DOWNLOAD_FOLDER, OUTPUT_BASE_FOLDER
from utils.file_utils import extract_text_from_story_folders


class ProcessStage:
    """处理阶段：处理下载的需求文件"""

    def __init__(self, input_folder: str = None, output_folder: str = None):
        """
        初始化处理阶段
        
        Args:
            input_folder: 输入文件夹，包含story_xxx格式的需求文件夹
            output_folder: 输出文件夹，用于保存提取的文本文件
        """
        self.input_folder = input_folder or DOWNLOAD_FOLDER
        self.output_folder = output_folder or OUTPUT_BASE_FOLDER

    def execute(self, story_ids: list = None, handler=None) -> bool:
        """执行处理阶段"""
        logging.info("开始执行处理阶段")
        logging.info(f"输入文件夹: {self.input_folder}")
        logging.info(f"输出文件夹: {self.output_folder}")

        try:
            # 调用 file_utils 中的方法提取文本
            extract_text_from_story_folders(self.input_folder, self.output_folder)
            logging.info("处理阶段执行完成")
            return True
        except Exception as e:
            logging.error(f"处理阶段执行失败: {str(e)}")
            return False


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    process_stage = ProcessStage()
    process_stage.execute()