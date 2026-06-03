import logging
import requests
import json
import os
from pathlib import Path
import concurrent.futures
import time
from typing import Tuple, Optional, List

from utils.file_utils import read_txt_file
from config.constants import (
    GPT_API_KEY, GPT_PROMPT_FILE, OUTPUT_BASE_FOLDER, JSON_DATA_PATH,
    GPT_PROVIDER, DEEPSEEK_MODEL, DEEPSEEK_API_URL,
    QWEN_MODEL, QWEN_API_URL, QWEN_API_KEY, QWEN_USER
)

logger = logging.getLogger(__name__)


class GptStage:
    """GPT处理阶段：调用GPT生成测试用例"""

    def __init__(self):
        self.provider = GPT_PROVIDER
        self.session = self._init_session()

    def _init_session(self) -> requests.Session:
        """初始化HTTP会话，复用连接"""
        session = requests.Session()
        if self.provider == "deepseek":
            session.headers.update({
                "Authorization": f"Bearer {GPT_API_KEY}",
                "Content-Type": "application/json",
                "Connection": "keep-alive"
            })
        elif self.provider == "qwen":
            session.headers.update({
                "Authorization": f"Bearer {QWEN_API_KEY}",
                "Content-Type": "application/json",
                "Connection": "keep-alive"
            })
        return session

    def _chat_with_deepseek(self, prompt: str, model: str = None) -> str:
        """调用DeepSeek API获取响应"""
        current_model = model or DEEPSEEK_MODEL
        content = read_txt_file(GPT_PROMPT_FILE)

        data = {
            "model": current_model,
            "messages": [
                {"role": "system", "content": content},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "stream": False
        }

        for retry in range(3):
            try:
                response = self.session.post(DEEPSEEK_API_URL, json=data, timeout=360)
                response.raise_for_status()
                response_data = response.json()
                return response_data['choices'][0]['message']['content']

            except requests.exceptions.HTTPError as e:
                logger.error(f"HTTP错误 ({retry+1}/3): {e.response.status_code}")
                time.sleep(2 ** retry)
            except requests.exceptions.ConnectionError as e:
                if "10054" in str(e):
                    logger.info(f"连接断开，正在重试 ({retry+1}/3)")
                else:
                    logger.error(f"连接错误 ({retry+1}/3): {str(e)}")
                time.sleep(2 ** retry)
            except Exception as e:
                logger.error(f"请求异常 ({retry+1}/3): {str(e)}")
                time.sleep(2 ** retry)

        return "多次重试后仍然失败"

    def _chat_with_qwen(self, prompt: str, model: str = None) -> str:
        """调用Qwen API获取响应（新接口格式）"""
        current_model = model or QWEN_MODEL
        content = read_txt_file(GPT_PROMPT_FILE)

        data = {
            "inputs": {},
            "query": f"{content}\n\n{prompt}",
            "response_mode": "blocking",
            "conversation_id": "",
            "user": QWEN_USER,
            "files": []
        }

        for retry in range(3):
            try:
                response = self.session.post(QWEN_API_URL, json=data, timeout=360)
                response.raise_for_status()
                response_data = response.json()
                return response_data.get('answer', '')

            except requests.exceptions.HTTPError as e:
                logger.error(f"HTTP错误 ({retry+1}/3): {e.response.status_code}")
                time.sleep(2 ** retry)
            except requests.exceptions.ConnectionError as e:
                if "10054" in str(e):
                    logger.info(f"连接断开，正在重试 ({retry+1}/3)")
                else:
                    logger.error(f"连接错误 ({retry+1}/3): {str(e)}")
                time.sleep(2 ** retry)
            except Exception as e:
                logger.error(f"请求异常 ({retry+1}/3): {str(e)}")
                time.sleep(2 ** retry)

        return "多次重试后仍然失败"

    def chat_with_gpt(self, prompt: str, model: str = None) -> str:
        """根据配置调用相应的GPT服务"""
        if self.provider == "deepseek":
            logger.info(f"使用DeepSeek GPT服务，模型: {model or DEEPSEEK_MODEL}")
            return self._chat_with_deepseek(prompt, model)
        elif self.provider == "qwen":
            logger.info(f"使用Qwen GPT服务，模型: {model or QWEN_MODEL}")
            return self._chat_with_qwen(prompt, model)
        else:
            logger.error(f"未知的GPT服务提供商: {self.provider}")
            return "未知的GPT服务提供商"

    def _parse_gpt_response(self, response_text: str) -> dict:
        """解析GPT响应，提取JSON内容"""
        response_text = response_text.strip()

        # 移除Qwen思考过程标签内容
        if "<think>" in response_text and "</think>" in response_text:
            think_start = response_text.find("<think>")
            think_end = response_text.find("</think>") + len("</think>")
            response_text = response_text[:think_start] + response_text[think_end:]
            response_text = response_text.strip()

        if "```json" in response_text:
            json_start = response_text.find("```json") + 7
            json_end = response_text.find("```", json_start)
            json_str = response_text[json_start:json_end].strip()
        elif "```" in response_text:
            json_start = response_text.find("```") + 3
            json_end = response_text.find("```", json_start)
            json_str = response_text[json_start:json_end].strip()
        else:
            json_str = response_text

        return json.loads(json_str)

    def process_single_file(self, file_info: Tuple[str, str], output_folder: str) -> Tuple[str, Optional[str], Optional[str]]:
        """处理单个文件"""
        filename, input_folder = file_info
        filepath = os.path.join(input_folder, filename)
        logger.info(f"正在处理文件: {filename}")

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                file_content = f.read()

            if not file_content.strip():
                logger.warning(f"文件 {filename} 内容为空，跳过")
                return filename, None, "文件内容为空"

            logger.info(f"文件 {filename} 内容长度: {len(file_content)} 字符")
            response = self.chat_with_gpt(file_content)

            try:
                test_cases_data = self._parse_gpt_response(response)
                output_path = self._save_test_cases(filename, test_cases_data, output_folder)
                logger.info(f"✓ 成功保存测试用例: {output_path}")
                return filename, output_path, None

            except json.JSONDecodeError as e:
                debug_path = self._save_debug_response(filename, response, output_folder)
                logger.error(f"✗ 文件 {filename} JSON解析失败: {str(e)}")
                return filename, None, f"JSON解析失败: {str(e)}"

        except Exception as e:
            logger.error(f"处理文件 {filename} 时出错: {str(e)}")
            return filename, None, f"处理错误: {str(e)}"

    def _save_test_cases(self, filename: str, data: dict, output_folder: str) -> str:
        """保存测试用例JSON文件"""
        base_name = os.path.splitext(filename)[0]
        output_filename = f"{base_name}.json"
        output_path = os.path.join(output_folder, output_filename)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return output_path

    def _save_debug_response(self, filename: str, response: str, output_folder: str) -> str:
        """保存调试响应文件"""
        debug_filename = f"{os.path.splitext(filename)[0]}_debug.txt"
        debug_path = os.path.join(output_folder, debug_filename)
        
        with open(debug_path, 'w', encoding='utf-8') as f:
            f.write(response)
        
        return debug_path

    def process_txt_files_to_gpt(self, input_folder: str, output_folder: str = "gpt_output", max_workers: int = 3, story_ids: list = None):
        """批量处理txt文件"""
        Path(output_folder).mkdir(exist_ok=True)
        
        # 获取所有txt文件
        all_txt_files = [f for f in os.listdir(input_folder) if f.endswith('.txt')]
        
        # 如果指定了story_ids，则只处理对应ID的文件
        if story_ids:
            # 构建需要处理的文件名集合 (story_id.txt)
            expected_files = {f"{story_id}.txt" for story_id in story_ids}
            txt_files = [f for f in all_txt_files if f in expected_files]
            
            # 检查是否有缺失的文件
            missing_files = expected_files - set(all_txt_files)
            if missing_files:
                logger.warning(f"以下需求对应的txt文件不存在: {missing_files}")
        else:
            txt_files = all_txt_files

        if not txt_files:
            logger.info(f"在文件夹 {input_folder} 中未找到需要处理的txt文件")
            return

        logger.info(f"找到 {len(txt_files)} 个txt文件，开始并行处理...")
        file_infos = [(filename, input_folder) for filename in txt_files]

        successful_files, failed_files = 0, 0

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_file = {
                executor.submit(self.process_single_file, file_info, output_folder): file_info[0]
                for file_info in file_infos
            }

            for future in concurrent.futures.as_completed(future_to_file):
                filename = future_to_file[future]
                try:
                    _, output_path, error = future.result()
                    if error:
                        failed_files += 1
                        logger.error(f"❌ 文件 {filename} 处理失败: {error}")
                    else:
                        successful_files += 1
                        logger.info(f"✅ 文件 {filename} 处理完成")
                except Exception as exc:
                    failed_files += 1
                    logger.error(f"❌ 文件 {filename} 生成异常: {exc}")

        logger.info(f"\n处理完成! 成功: {successful_files}, 失败: {failed_files}, 输出: {output_folder}")

    def execute(self, story_ids: list = None, input_folder: str = None, output_folder: str = None, max_workers: int = 3, handler=None) -> bool:
        """执行GPT处理阶段"""
        logger.info("开始执行GPT处理阶段")

        try:
            actual_input = input_folder if input_folder else OUTPUT_BASE_FOLDER
            actual_output = output_folder if output_folder else JSON_DATA_PATH
            
            logger.info(f"输入文件夹: {actual_input}")
            logger.info(f"输出文件夹: {actual_output}")
            
            # 根据story_ids过滤要处理的文件
            self.process_txt_files_to_gpt(actual_input, actual_output, max_workers, story_ids)
            logger.info("GPT处理阶段执行完成")
            return True
        except Exception as e:
            logger.error(f"GPT处理阶段执行失败: {str(e)}")
            return False


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    gpt_stage = GptStage()
    gpt_stage.execute()