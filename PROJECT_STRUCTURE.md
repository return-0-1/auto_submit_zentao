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
├── config/                         # 配置模块
│   ├── __init__.py
│   └── constants.py                # 常量定义与配置
├── core/                           # 核心业务模块
│   ├── __init__.py
│   ├── business_handler.py         # 业务处理逻辑
│   └── page_operations.py          # 页面操作封装
├── utils/                          # 工具模块
│   ├── __init__.py
│   └── file_utils.py               # 文件操作工具函数
├── workflow/                       # 工作流模块
│   ├── __init__.py
│   ├── download_stage.py           # 下载阶段处理
│   ├── gpt_stage.py                # GPT处理阶段
│   ├── process_stage.py            # 处理阶段
│   ├── submit_stage.py             # 提交阶段
│   └── workflow_manager.py         # 工作流管理器
├── PROJECT_STRUCTURE.md            # 项目结构文档
└── main.py                         # 程序主入口
```

## 文件说明

### main.py
程序主入口文件，负责初始化工作流管理器并启动自动化流程。

### config/constants.py
系统常量与配置定义。

**包含内容：**
- URL 配置（禅道系统地址）
- 浏览器驱动路径
- 默认配置参数
- 产品ID映射字典 `PRODUCT_DICT`

### core/business_handler.py
核心业务处理模块，包含两个主要类：

**FormFiller 类**
- `fill_test_case()` - 填写测试用例表单
- `fill_bug_report()` - 填写缺陷报告表单

**BusinessHandler 类**
- 处理业务逻辑，协调页面操作和数据读取

### core/page_operations.py
页面操作封装类，使用 Selenium WebDriver 进行浏览器自动化操作。

**核心功能：**
- `init_driver()` - 初始化 Edge 浏览器驱动
- `login()` - 登录系统
- `select_chosen_option()` - 选择 Chosen 下拉框选项
- `submit_form()` - 提交表单

### utils/file_utils.py
通用工具函数模块。

**提供功能：**
- `read_json_file()` - 安全读取 JSON 文件
- 文件相关的辅助工具函数

### workflow/workflow_manager.py
工作流管理器，负责协调各个阶段的执行顺序。

### workflow/download_stage.py
下载阶段处理，负责从禅道系统下载相关数据。

### workflow/gpt_stage.py
GPT处理阶段，利用AI生成测试用例或缺陷描述。

### workflow/process_stage.py
处理阶段，对下载的数据进行处理和转换。

### workflow/submit_stage.py
提交阶段，将处理后的数据提交到禅道系统。

## 依赖技术

- **Selenium WebDriver** - 浏览器自动化
- **Win32 API** - Windows 系统交互
- **JSON** - 数据解析

## 用途

本项目用于自动化提交测试用例和缺陷报告到禅道（ZenTao）项目管理系统，减少人工操作工作量。