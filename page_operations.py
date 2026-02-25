import logging
import time
from typing import Optional
from selenium import webdriver
from selenium.common import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from constants import DRIVER_PATH
from constants import NEED_URL


class PageOperator:
    """页面操作封装类，处理浏览器驱动、元素操作、登录等"""

    def __init__(self):
        self.driver: Optional[webdriver.Edge] = None

    def init_driver(self) -> webdriver.Edge:
        """初始化Edge浏览器驱动"""
        try:
            self.driver = webdriver.Edge(service=Service(DRIVER_PATH))
            self.driver.implicitly_wait(10)  # 隐式等待
            return self.driver
        except Exception as e:
            logging.error(f"初始化浏览器驱动失败: {e}")
            raise

    def login(self, url: str, account: str, password: str) -> None:
        """登录系统"""
        if not self.driver:
            self.init_driver()

        try:
            self.driver.get(url)
            # 输入账号密码并提交
            self.driver.find_element(By.NAME, "account").send_keys(account)
            self.driver.find_element(By.NAME, "password").send_keys(password)
            self.driver.find_element(By.ID, "submit").click()
            logging.info("登录成功")
        except Exception as e:
            logging.error(f"登录失败: {e}")
            raise

    def select_chosen_option(self, selector: str, target_text: str) -> bool:
        """
        选择Chosen下拉框的选项（优化版）
        :param selector: 下拉框触发按钮的CSS选择器
        :param target_text: 要选择的选项文本
        :return: 是否选中成功
        """
        # 校验驱动是否初始化
        if not self.driver:
            raise RuntimeError("浏览器驱动未初始化")

        try:
            # 1. 等待触发按钮可点击并点击（替换原直接find_element，增强稳定性）
            trigger_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
            )
            trigger_button.click()

            # 2. 等待选项列表加载完成且第一个选项可点击（精准等待，替代仅presence检查）
            results_locator = (By.CSS_SELECTOR, "ul.chosen-results li")
            # WebDriverWait(self.driver, 10).until(
            #     EC.element_to_be_clickable(results_locator)
            # )
            # 短暂等待所有选项渲染完成（应对异步加载的边界情况）
            time.sleep(0.3)

            # 3. 遍历选项并点击匹配项（保留原逻辑，优化日志）
            li_elements = self.driver.find_elements(*results_locator)
            for element in li_elements:
                element_text = element.text.strip()  # 去除首尾空格，避免匹配失败
                if target_text in element_text:
                    # 确保元素可点击后再点击
                    WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable(element)
                    ).click()
                    logging.info(f"成功选中Chosen下拉框选项: {target_text}")
                    return True

            # 未找到匹配选项的日志和返回
            logging.warning(f"在Chosen下拉框中未找到匹配的选项: {target_text}")
            return False

        except TimeoutException:
            logging.error(f"选择Chosen下拉框选项超时：触发按钮选择器[{selector}]，目标文本[{target_text}]")
            return False
            # raise
        except NoSuchElementException:
            logging.error(f"选择Chosen下拉框选项失败：未找到触发按钮[{selector}]或选项列表")
            raise
        except Exception as e:
            logging.error(f"选择Chosen下拉框选项异常: {str(e)}")
            raise

    def submit_form(self) -> None:
        """提交表单"""
        if not self.driver:
            raise RuntimeError("浏览器驱动未初始化")

        try:
            submit_btn = self.driver.find_element(By.ID, "submit")
            # 滚动到按钮可见
            self.driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
            submit_btn.click()
            logging.info("表单提交成功")
        except Exception as e:
            logging.error(f"表单提交失败: {e}")
            raise

    def get_product_name(self, story_id) -> str:
        """获取页面上的产品名称"""
        if not self.driver:
            raise RuntimeError("浏览器驱动未初始化")
        try:
            url = NEED_URL + story_id
            time.sleep(0.6)
            self.driver.get(url)
            wait = WebDriverWait(self.driver, 10)
            product_th = wait.until(EC.presence_of_element_located((By.XPATH, "//th[text()='所属产品']")))
            product_td = product_th.find_element(By.XPATH, "./following-sibling::td[1]")
            product_name = product_td.find_element(By.TAG_NAME, "a").text.strip()
            logging.info(f"获取到产品名称: {product_name}")
            return product_name
        except Exception as e:
            logging.error(f"获取产品名称失败: {e}")
            raise

    def close_driver(self) -> None:
        """关闭浏览器驱动"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            logging.info("浏览器驱动已关闭")
