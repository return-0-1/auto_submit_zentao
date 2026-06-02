import logging
from typing import Dict, Any, List
from selenium.webdriver.common.by import By
from config.constants import JSON_DATA_PATH, PRODUCT_DICT
from utils.file_utils import read_json_file, get_url_by_type
from core.page_operations import PageOperator


class FormFiller:
    """表单填写业务逻辑类"""

    def __init__(self, page_operator: PageOperator):
        self.page_operator = page_operator

    def fill_test_case(self, url: str, module: str, demand: str, data: Dict[str, Any], product: str) -> None:
        """填写测试用例表单"""
        if not self.page_operator.driver:
            raise RuntimeError("浏览器驱动未初始化")

        for single in data.values():
            try:
                product_id = PRODUCT_DICT.get(product)
                url = f"http://192.168.7.3:82/index.php?m=testcase&f=create&productID={product_id}&branch=0&moduleID=0"
                self.page_operator.driver.get(url)
                title = single.get("标题", "")
                steps = single.get("步骤", {})
                expects = single.get("预期", {})

                self.page_operator.driver.find_element(By.NAME, "title").send_keys(title)

                for key, value in steps.items():
                    step_elem = self.page_operator.driver.find_element(By.NAME, f"steps[{key}]")
                    step_elem.send_keys(value)
                    self.page_operator.driver.find_element(By.TAG_NAME, "body").click()

                for key, value in expects.items():
                    expect_elem = self.page_operator.driver.find_element(By.NAME, f"expects[{key}]")
                    expect_elem.send_keys(value)

                self.page_operator.select_chosen_option("#module_chosen > a.chosen-single", module)
                is_demand_selected = self.page_operator.select_chosen_option("#story_chosen > a.chosen-single", demand)

                if is_demand_selected:
                    logging.info(f"需求 {demand} 选中成功，提交表单")
                    self.page_operator.submit_form()
                else:
                    logging.warning(f"需求 {demand} 选中失败，等待用户操作")
                    while True:
                        user_input = input("请输入 Y 继续提交，N 放弃提交: ").strip().upper()
                        if user_input == "Y":
                            logging.warning(f"需求 {demand} 执行手动提交")
                            self.page_operator.submit_form()
                            break
                        elif user_input == "N":
                            logging.warning(f"需求 {demand} 放弃提交")
                            break
                        else:
                            logging.warning("输入无效，请重新输入")
            except Exception as e:
                logging.error(f"填写测试用例失败: {e}")
                raise

    def fill_bug_report(self, url: str, module: str, demand: str, data: Dict[str, Any], product: str) -> None:
        """填写缺陷报告表单"""
        if not self.page_operator.driver:
            raise RuntimeError("浏览器驱动未初始化")

        for single in data.values():
            try:
                self.page_operator.driver.get(url)
                title = single.get("标题", "")

                self.page_operator.driver.find_element(By.NAME, "title").send_keys(title)

                self.page_operator.select_chosen_option("#module_chosen > a.chosen-single", module)
                self.page_operator.select_chosen_option("#product_chosen > a.chosen-single", product)
                is_demand_selected = self.page_operator.select_chosen_option("#story_chosen > a.chosen-single", demand)

                if is_demand_selected:
                    self.page_operator.submit_form()
                else:
                    logging.warning(f"需求 {demand} 选中失败，跳过提交")

            except Exception as e:
                logging.error(f"填写缺陷报告失败: {e}")
                raise


class BusinessHandler:
    """核心业务处理类"""

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.page_operator = PageOperator()
        self.form_filler = FormFiller(self.page_operator)
        self.is_logged_in = False

    def login(self, url: str) -> None:
        """登录系统（复用会话）"""
        if not self.is_logged_in:
            self.page_operator.login(url, self.username, self.password)
            self.is_logged_in = True
            logging.info("已建立登录会话")

    def process_file(self, story_id: str, submit_type: str, module: str) -> None:
        """处理单个JSON文件，填写对应表单"""
        try:
            json_file = story_id + ".json"
            target_url = get_url_by_type(submit_type)
            if not target_url:
                raise ValueError(f"无效的提交类型: {submit_type}")

            self.login(target_url)
            product = self.page_operator.get_product_name(story_id)
            data = read_json_file(f"{JSON_DATA_PATH}{json_file}")

            if submit_type == "case":
                self.form_filler.fill_test_case(target_url, module, story_id, data, product)
            elif submit_type == "bug":
                self.form_filler.fill_bug_report(target_url, module, story_id, data, product)

            logging.info(f"文件 {story_id} 处理完成")

        except Exception as e:
            logging.error(f"处理文件 {story_id} 失败: {e}")
            raise

    def close(self) -> None:
        """关闭浏览器和会话"""
        self.page_operator.close_driver()
        self.is_logged_in = False

    def download_story_files(self, story_ids: List[str], download_folder: str) -> None:
        """
        下载需求相关的文件

        Args:
            story_ids: 需求ID列表
            download_folder: 下载文件夹路径
        """
        try:
            from config import CASE_URL
            self.page_operator.login(CASE_URL, self.username, self.password)
            self.page_operator.download_story_files(story_ids, download_folder)
            logging.info("下载任务完成")
        except Exception as e:
            logging.error(f"下载需求文件失败: {e}")
            raise
        finally:
            self.page_operator.close_driver()
