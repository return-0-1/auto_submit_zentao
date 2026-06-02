import requests
import logging
from typing import Dict, Optional, List
from requests.exceptions import RequestException


from config.constants import ZENTAO_BASE_URL


class ZenTaoApiSubmitter:
    """
    禅道 API 提交器 - 使用 requests 直接发送 POST 请求
    替代原来基于 Selenium 的页面操作方式，更快速、更轻量
    """
    
    def __init__(self, base_url: str = None):
        """
        初始化提交器
        
        :param base_url: 禅道服务器地址，默认使用配置文件中的地址
        """
        self.base_url = (base_url or ZENTAO_BASE_URL).rstrip('/')
        self.session = requests.Session()
        self.session.verify = False  # 禁用 SSL 验证
        
        # 设置默认请求头
        self.headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Origin': self.base_url,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'X-Requested-With': 'XMLHttpRequest',
        }
        self.session.headers.update(self.headers)
        self.is_logged_in = False
        
    def login(self, username: str, password: str) -> bool:
        """
        使用用户名密码登录禅道
        
        :param username: 用户名
        :param password: 密码
        :return: 是否登录成功
        """
        if self.is_logged_in:
            logging.info("已登录，跳过重复登录")
            return True
            
        try:
            login_url = f"{self.base_url}/index.php?m=user&f=login"
            
            # 先获取会话
            self.session.get(login_url)
            
            # 发送登录请求
            payload = {
                'account': username,
                'password': password,
                'keepLogin': '1'
            }
            
            response = self.session.post(login_url, data=payload, allow_redirects=False)
            
            # 检查是否登录成功（通过检查重定向或响应内容）
            if response.status_code == 302 or response.status_code == 200:
                # 验证登录状态
                test_response = self.session.get(f"{self.base_url}/index.php?m=user&f=profile")
                if test_response.status_code == 200 and 'login' not in test_response.url:
                    self.is_logged_in = True
                    logging.info("登录成功")
                    return True
            
            logging.error(f"登录失败，状态码: {response.status_code}")
            return False
            
        except RequestException as e:
            logging.error(f"登录过程发生异常: {str(e)}")
            return False
    
    def get_product_name(self, story_id: str) -> str:
        """
        获取需求所属产品名称
        
        :param story_id: 需求ID
        :return: 产品名称
        """
        try:
            url = f"{self.base_url}/index.php?m=story&f=view&t=html&id={story_id}"
            response = self.session.get(url)
            
            if response.status_code == 200:
                # 从HTML中提取产品名称
                import re
                match = re.search(r'<th[^>]*>所属产品</th>\s*<td[^>]*>\s*<a[^>]*>([^<]+)</a>', response.text)
                if match:
                    product_name = match.group(1).strip()
                    logging.info(f"获取到需求 {story_id} 的产品名称: {product_name}")
                    return product_name
            
            logging.error(f"获取产品名称失败，需求ID: {story_id}")
            return ""
            
        except Exception as e:
            logging.error(f"获取产品名称异常: {str(e)}")
            return ""
    
    def submit_testcase(self,
                       product_id: int,
                       title: str,
                       steps: Dict[str, str],
                       expects: Dict[str, str],
                       module_id: int = 0,
                       story_id: str = "",
                       case_type: str = "feature",
                       priority: int = 3,
                       debug_mode: bool = False) -> bool:
        """
        提交单个测试用例
        
        :param product_id: 产品ID
        :param title: 测试用例标题
        :param steps: 步骤字典 {步骤编号: 步骤内容}
        :param expects: 预期结果字典 {步骤编号: 预期内容}
        :param module_id: 模块ID
        :param story_id: 关联需求ID
        :param case_type: 用例类型
        :param priority: 优先级
        :param debug_mode: 是否调试模式
        :return: 是否提交成功
        """
        if debug_mode:
            logging.info(f"[调试模式] 测试用例 {title} 未实际提交")
            return True
            
        # 构造请求参数
        params = {
            'm': 'testcase',
            'f': 'create',
            'productID': str(product_id),
            'branch': '0',
            'moduleID': str(module_id),
        }
        
        # 构造表单数据（multipart/form-data 格式）
        files = {
            'product': (None, str(product_id)),
            'module': (None, str(module_id)),
            'type': (None, case_type),
            'stage[]': (None, ''),
            'story': (None, story_id),
            'title': (None, title),
            'color': (None, ''),
            'pri': (None, str(priority)),
            'precondition': (None, ''),
            'keywords': (None, ''),
            'status': (None, 'wait'),
            'labels[]': (None, ''),
            'files[]': (None, ''),
        }
        
        # 添加步骤和预期结果
        # 获取所有步骤编号并排序
        all_keys = set(steps.keys()).union(set(expects.keys()))
        sorted_keys = sorted(all_keys, key=lambda x: int(x))
        
        for key in sorted_keys:
            step_content = steps.get(key, '')
            expect_content = expects.get(key, '')
            step_type = 'step' if expect_content else 'item'
            
            files[f'steps[{key}]'] = (None, step_content)
            files[f'stepType[{key}]'] = (None, step_type)
            files[f'expects[{key}]'] = (None, expect_content)
        
        try:
            logging.info(f"正在提交测试用例: {title}")
            
            response = self.session.post(
                f"{self.base_url}/index.php",
                params=params,
                files=files
            )
            
            logging.debug(f"响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                # 检查是否成功
                if '成功' in response.text or 'testcaseID' in response.text:
                    logging.info(f"✅ 测试用例提交成功: {title}")
                    return True
                logging.warning(f"提交结果不确定，响应内容: {response.text[:500]}")
                return True
            
            logging.error(f"❌ 测试用例提交失败，状态码: {response.status_code}")
            return False
            
        except RequestException as e:
            logging.error(f"❌ 提交测试用例异常: {str(e)}")
            return False
    
    def submit_bug_report(self,
                         product_id: int,
                         title: str,
                         module_id: int = 0,
                         story_id: str = "",
                         debug_mode: bool = False) -> bool:
        """
        提交缺陷报告
        
        :param product_id: 产品ID
        :param title: 缺陷标题
        :param module_id: 模块ID
        :param story_id: 关联需求ID
        :param debug_mode: 是否调试模式
        :return: 是否提交成功
        """
        if debug_mode:
            logging.info(f"[调试模式] 缺陷报告 {title} 未实际提交")
            return True
            
        params = {
            'm': 'bug',
            'f': 'create',
            'productID': str(product_id),
            'branch': '0',
            'extra': f'moduleID={module_id}',
        }
        
        files = {
            'product': (None, str(product_id)),
            'module': (None, str(module_id)),
            'story': (None, story_id),
            'title': (None, title),
            'type': (None, 'code'),
            'pri': (None, '3'),
            'severity': (None, '3'),
            'status': (None, 'active'),
            'labels[]': (None, ''),
            'files[]': (None, ''),
        }
        
        try:
            logging.info(f"正在提交缺陷报告: {title}")
            
            response = self.session.post(
                f"{self.base_url}/index.php",
                params=params,
                files=files
            )
            
            if response.status_code == 200 and '成功' in response.text:
                logging.info(f"✅ 缺陷报告提交成功: {title}")
                return True
            
            logging.error(f"❌ 缺陷报告提交失败")
            return False
            
        except RequestException as e:
            logging.error(f"❌ 提交缺陷报告异常: {str(e)}")
            return False
    
    def close(self):
        """关闭会话"""
        self.session.close()
        self.is_logged_in = False
        logging.info("会话已关闭")