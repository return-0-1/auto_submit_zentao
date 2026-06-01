# auto_submit_zentao 项目结构

## 目录结构

```
auto_submit_zentao/
├── .idea/                          # PyCharm IDE 配置目录
│   ├── inspectionProfiles/
│   │   ├── Project_Default.xml
│   │   └── profiles_settings.xml
│   ├── auto_submit_zentao.iml
│   ├── misc.xml
│   ├── modules.xml
│   ├── vcs.xml
│   └── workspace.xml
├── business_handler.py              # 业务处理逻辑
├── constants.py                     # 常量定义与配置
├── main.py                          # 程序主入口
├── page_operations.py               # 页面操作封装
└── utils.py                         # 工具函数
```

## 文件说明

### main.py
程序主入口文件，负责初始化业务处理器并处理指定的JSON文件。

**核心功能：**
- 初始化 `BusinessHandler` 实例
- 遍历 `DEFAULT_STORY_ID_LIST` 中的每个需求ID
- 调用 `process_file()` 方法处理文件

### business_handler.py
核心业务处理模块，包含两个主要类：

**FormFiller 类**
- `fill_test_case()` - 填写测试用例表单
- `fill_bug_report()` - 填写缺陷报告表单

**BusinessHandler 类**
- 处理业务逻辑，协调页面操作和数据读取

### page_operations.py
页面操作封装类，使用 Selenium WebDriver 进行浏览器自动化操作。

**核心功能：**
- `init_driver()` - 初始化 Edge 浏览器驱动
- `login()` - 登录系统
- `select_chosen_option()` - 选择 Chosen 下拉框选项
- `submit_form()` - 提交表单

### constants.py
系统常量与配置定义。

**包含内容：**
- URL 配置（禅道系统地址）
- 浏览器驱动路径
- 默认配置参数
- 产品ID映射字典 `PRODUCT_DICT`

### utils.py
通用工具函数模块。

**提供功能：**
- `read_json_file()` - 安全读取 JSON 文件
- `get_url_by_type()` - 根据提交类型获取对应URL

## 依赖技术

- **Selenium WebDriver** - 浏览器自动化
- **Win32 API** - Windows 系统交互
- **JSON** - 数据解析

## 用途

本项目用于自动化提交测试用例和缺陷报告到禅道（ZenTao）项目管理系统，减少人工操作工作量。
