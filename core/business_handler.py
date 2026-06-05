import logging
from typing import Dict, Any, List
from config.constants import JSON_DATA_PATH, PRODUCT_DICT, DEBUG_MODE, NEED_URL, CASE_URL
from utils.file_utils import read_json_file, get_url_by_type
from core.api_submitter import ZenTaoApiSubmitter


class BusinessHandler:
    """核心业务处理类 - Selenium登录 + requests提交"""

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.api_submitter = ZenTaoApiSubmitter()
        self.is_logged_in = False
        self.page_operator = None

    def login(self, url: str = None) -> None:
        """登录系统 - 使用Selenium登录，然后将cookies同步到requests session"""
        if not self.is_logged_in:
            from core.page_operations import PageOperator
            
            # 使用Selenium登录 - 优先使用传入的url，否则使用默认的CASE_URL
            login_url = url or CASE_URL
            self.page_operator = PageOperator()
            self.page_operator.init_driver()
            self.page_operator.login(login_url, self.username, self.password)
            logging.info("Selenium登录成功")
            
            # 获取浏览器cookies并同步到requests session
            browser_cookies = self.page_operator.driver.get_cookies()
            for cookie in browser_cookies:
                self.api_submitter.session.cookies.set(cookie['name'], cookie['value'], domain=cookie.get('domain'))
            
            self.api_submitter.is_logged_in = True
            self.is_logged_in = True
            logging.info("已将浏览器cookies同步到requests session")

    def process_file(self, story_id: str, submit_type: str, module: str) -> None:
        """处理单个JSON文件，填写对应表单"""
        try:
            json_file = story_id + ".json"
            target_url = get_url_by_type(submit_type)
            if not target_url:
                raise ValueError(f"无效的提交类型: {submit_type}")

            self.login(target_url)
            
            # 获取产品名称 - 使用Selenium浏览器获取，避免requests被重定向到重置密码页面
            product = self.page_operator.get_product_name(story_id)
            if not product:
                logging.warning(f"无法获取需求 {story_id} 的产品名称")
                return
            
            # 获取产品ID
            product_id = PRODUCT_DICT.get(product)
            if not product_id:
                logging.warning(f"未找到产品 {product} 的ID映射")
                return
            
            # 读取JSON数据
            data = read_json_file(f"{JSON_DATA_PATH}{json_file}")

            # 根据类型提交
            if submit_type == "case":
                self._submit_testcase(product_id, story_id, module, data)
            elif submit_type == "bug":
                self._submit_bug(product_id, story_id, module, data)

            logging.info(f"文件 {story_id} 处理完成")

        except Exception as e:
            logging.error(f"处理文件 {story_id} 失败: {e}")
            raise

    def _submit_testcase(self, product_id: int, story_id: str, module: str, data: Dict[str, Any]) -> None:
        """提交测试用例"""
        for single in data.values():
            try:
                title = single.get("标题", "")
                steps = single.get("步骤", {})
                expects = single.get("预期", {})

                if not title:
                    logging.warning("测试用例标题为空，跳过")
                    continue

                success = self.api_submitter.submit_testcase(
                    product_id=product_id,
                    title=title,
                    steps=steps,
                    expects=expects,
                    module_id=0,  # 模块ID暂时设为0，可根据需要修改
                    story_id=story_id,
                    case_type="feature",
                    priority=3,
                    debug_mode=DEBUG_MODE
                )

                if not success:
                    logging.warning(f"测试用例 {title} 提交失败")

            except Exception as e:
                logging.error(f"提交测试用例失败: {e}")
                raise

    def _submit_bug(self, product_id: int, story_id: str, module: str, data: Dict[str, Any]) -> None:
        """提交缺陷报告"""
        for single in data.values():
            try:
                title = single.get("标题", "")

                if not title:
                    logging.warning("缺陷标题为空，跳过")
                    continue

                success = self.api_submitter.submit_bug_report(
                    product_id=product_id,
                    title=title,
                    module_id=0,
                    story_id=story_id,
                    debug_mode=DEBUG_MODE
                )

                if not success:
                    logging.warning(f"缺陷报告 {title} 提交失败")

            except Exception as e:
                logging.error(f"提交缺陷报告失败: {e}")
                raise

    def close(self) -> None:
        """关闭会话 - 同时关闭requests session和浏览器"""
        self.api_submitter.close()
        
        # 关闭浏览器
        if self.page_operator:
            self.page_operator.close_driver()
            self.page_operator = None
        
        self.is_logged_in = False

    def download_story_files(self, story_ids: List[str], download_folder: str) -> None:
        """
        下载需求相关的文件（复用已登录的浏览器会话）
        
        Args:
            story_ids: 需求ID列表
            download_folder: 下载文件夹路径
        """
        try:
            # 确保已登录
            self.login()
            
            # 使用已登录的浏览器会话执行下载
            self.page_operator.download_story_files(story_ids, download_folder)
            logging.info("下载任务完成")
            
        except Exception as e:
            logging.error(f"下载需求文件失败: {e}")
            raise