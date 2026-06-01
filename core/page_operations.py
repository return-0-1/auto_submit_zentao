import logging
import os
import time
import requests
from typing import Optional, List
from selenium import webdriver
from selenium.common import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import DRIVER_PATH, NEED_URL
from utils import clean_filename


class PageOperator:
    """页面操作封装类，处理浏览器驱动、元素操作、登录等"""

    def __init__(self):
        self.driver: Optional[webdriver.Edge] = None

    def init_driver(self) -> webdriver.Edge:
        """初始化Edge浏览器驱动"""
        try:
            self.driver = webdriver.Edge(service=Service(DRIVER_PATH))
            self.driver.implicitly_wait(10)
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
        if not self.driver:
            raise RuntimeError("浏览器驱动未初始化")

        try:
            trigger_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
            )
            trigger_button.click()

            results_locator = (By.CSS_SELECTOR, "ul.chosen-results li")
            time.sleep(0.3)

            li_elements = self.driver.find_elements(*results_locator)
            for element in li_elements:
                element_text = element.text.strip()
                if target_text in element_text:
                    WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable(element)
                    ).click()
                    logging.info(f"成功选中Chosen下拉框选项: {target_text}")
                    return True

            logging.warning(f"在Chosen下拉框中未找到匹配的选项: {target_text}")
            return False

        except TimeoutException:
            logging.error(f"选择Chosen下拉框选项超时：触发按钮选择器[{selector}]，目标文本[{target_text}]")
            return False
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

    def download_story_files(self, story_ids: List[str], download_folder: str) -> None:
        """
        下载需求相关的文件，清理文件名中的多余信息

        Args:
            story_ids: 需求ID数组
            download_folder: 下载文件夹路径
        """
        if not self.driver:
            raise RuntimeError("浏览器驱动未初始化")

        if not os.path.exists(download_folder):
            os.makedirs(download_folder)

        for story_id in story_ids:
            try:
                time.sleep(1)
                url = f"{NEED_URL}{story_id}"

                logging.info(f"正在访问需求 {story_id} 的页面...")
                self.driver.get(url)

                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )

                files_list = self.driver.find_elements(By.CSS_SELECTOR, "ul.files-list li")

                if not files_list:
                    logging.info(f"需求 {story_id} 没有找到文件")
                    continue

                logging.info(f"需求 {story_id} 找到 {len(files_list)} 个文件")

                story_folder = os.path.join(download_folder, f"story_{story_id}")
                if not os.path.exists(story_folder):
                    os.makedirs(story_folder)

                downloaded_count = 0
                for file_item in files_list:
                    try:
                        download_link = file_item.find_element(By.TAG_NAME, "a")
                        raw_file_name = download_link.text.strip()
                        file_url = download_link.get_attribute("href")

                        if file_url and raw_file_name:
                            clean_file_name = clean_filename(raw_file_name)
                            local_file_path = os.path.join(story_folder, clean_file_name)

                            logging.info(f"原始文件名: {raw_file_name}")
                            logging.info(f"清理后文件名: {clean_file_name}")
                            logging.info(f"正在下载: {clean_file_name}")

                            try:
                                selenium_cookies = self.driver.get_cookies()
                                session = requests.Session()

                                for cookie in selenium_cookies:
                                    session.cookies.set(cookie['name'], cookie['value'])

                                headers = {
                                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                                }

                                response = session.get(file_url, headers=headers, stream=True)
                                response.raise_for_status()

                                with open(local_file_path, 'wb') as f:
                                    for chunk in response.iter_content(chunk_size=8192):
                                        if chunk:
                                            f.write(chunk)

                                downloaded_count += 1
                                logging.info(f"✓ 成功下载: {clean_file_name}")

                            except Exception as download_error:
                                logging.error(f"✗ 下载失败 {clean_file_name}: {str(download_error)}")

                            time.sleep(1)

                    except Exception as e:
                        logging.error(f"处理文件时出错: {str(e)}")
                        continue

                logging.info(f"需求 {story_id} 的文件下载完成: {downloaded_count}/{len(files_list)}")

            except Exception as e:
                logging.error(f"处理需求 {story_id} 时出错: {str(e)}")
                continue

        logging.info("所有需求文件下载任务完成")
