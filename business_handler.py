import logging
from typing import Dict, Any
from constants import JSON_DATA_PATH
from utils import read_json_file
from page_operations import PageOperator
from selenium.webdriver.common.by import By


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
                from constants import PRODUCT_DICT
                product_id = PRODUCT_DICT.get(product)  # 默认值为4
                url = f"http://192.168.7.3:82/index.php?m=testcase&f=create&productID={product_id}&branch=0&moduleID=0"
                self.page_operator.driver.get(url)  # 重新加载表单页面
                title = single.get("标题", "")
                steps = single.get("步骤", {})
                expects = single.get("预期", {})

                # 填写标题
                self.page_operator.driver.find_element(By.NAME, "title").send_keys(title)

                # 填写步骤
                for key, value in steps.items():
                    step_elem = self.page_operator.driver.find_element(By.NAME, f"steps[{key}]")
                    step_elem.send_keys(value)
                    self.page_operator.driver.find_element(By.TAG_NAME, "body").click()  # 失去焦点

                # 填写预期结果
                for key, value in expects.items():
                    expect_elem = self.page_operator.driver.find_element(By.NAME, f"expects[{key}]")
                    expect_elem.send_keys(value)

                # 选择下拉框选项
                self.page_operator.select_chosen_option("#module_chosen > a.chosen-single", module)
                # self.page_operator.select_chosen_option("#product_chosen > a.chosen-single", product)
                is_demand_selected = self.page_operator.select_chosen_option("#story_chosen > a.chosen-single", demand)

                # 验证并提交
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
                self.page_operator.driver.get(url)  # 重新加载表单页面
                title = single.get("标题", "")

                # 填写标题
                self.page_operator.driver.find_element(By.NAME, "title").send_keys(title)

                # 选择下拉框选项
                self.page_operator.select_chosen_option("#module_chosen > a.chosen-single", module)
                self.page_operator.select_chosen_option("#product_chosen > a.chosen-single", product)
                is_demand_selected = self.page_operator.select_chosen_option("#story_chosen > a.chosen-single", demand)

                # 提交表单
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

    def process_file(self, story_id: str, submit_type: str, module: str) -> None:
        """处理单个JSON文件，填写对应表单"""
        try:
            # 解析需求名称
            json_file = story_id + ".json"

            # 获取目标URL并登录
            from utils import get_url_by_type
            target_url = get_url_by_type(submit_type)
            if not target_url:
                raise ValueError(f"无效的提交类型: {submit_type}")

            self.page_operator.login(target_url, self.username, self.password)

            # 获取产品名称
            product = self.page_operator.get_product_name(story_id)

            # 读取JSON数据
            data = read_json_file(f"{JSON_DATA_PATH}{json_file}")

            # 根据类型填写表单
            if submit_type == "case":
                self.form_filler.fill_test_case(target_url, module, story_id, data, product)
            elif submit_type == "bug":
                self.form_filler.fill_bug_report(target_url, module, story_id, data, product)

            logging.info(f"文件 {story_id} 处理完成")

        except Exception as e:
            logging.error(f"处理文件 {story_id} 失败: {e}")
            raise
        finally:
            self.page_operator.close_driver()
