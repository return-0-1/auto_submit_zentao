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
│   ├── page_operations.py          # 页面操作封装（Selenium）
│   └── api_submitter.py            # API提交器（requests）
├── utils/                          # 工具模块
│   ├── __init__.py
│   └── file_utils.py               # 文件操作工具函数
├── workflow/                       # 工作流模块
│   ├── __init__.py
│   ├── download_stage.py           # 下载阶段处理
│   ├── gpt_stage.py                # GPT处理阶段
│   ├── process_stage.py            # 处理阶段
│   ├── submit_stage.py             # 提交阶段
│   ├── workflow_manager.py         # 工作流管理器
│   └── state_manager.py            # 状态管理器
├── PROJECT_STRUCTURE.md            # 项目结构文档
├── README.md                       # 项目说明文档
└── main.py                         # 程序主入口
```

## 文件说明

### main.py
程序主入口文件，解析命令行参数，初始化工作流管理器并启动自动化流程。

### config/constants.py
系统常量与配置定义。

**包含内容：**
- URL 配置（禅道系统地址 `ZENTAO_BASE_URL`）
- 浏览器驱动路径 `DRIVER_PATH`
- 登录配置（`USERNAME`, `PASSWORD`）
- GPT API 配置（`GPT_API_KEY`, `GPT_API_URL`, `GPT_MODEL`）
- 路径配置（`DOWNLOAD_FOLDER`, `OUTPUT_BASE_FOLDER`, `JSON_DATA_PATH`）
- 调试模式 `DEBUG_MODE`
- 默认需求ID列表 `DEFAULT_STORY_ID_LIST`
- 产品ID映射字典 `PRODUCT_DICT`

### core/business_handler.py
核心业务处理模块。

**BusinessHandler 类**
- `__init__()` - 初始化业务处理器
- `login()` - 登录系统（使用 Selenium 登录，cookies 同步到 requests）
- `process_file()` - 处理单个需求文件
- `_submit_testcase()` - 提交测试用例
- `_submit_bug()` - 提交缺陷报告
- `download_story_files()` - 下载需求文件
- `close()` - 关闭会话

### core/page_operations.py
页面操作封装类，使用 Selenium WebDriver 进行浏览器自动化操作。

**核心功能：**
- `init_driver()` - 初始化 Edge 浏览器驱动（启动时自动最小化）
- `login()` - 登录系统
- `download_story_files()` - 下载需求文件
- `close_driver()` - 关闭浏览器

### core/api_submitter.py
API提交器，使用 requests 库直接发送 HTTP 请求。

**核心功能：**
- `login()` - 使用 requests 登录（备用）
- `get_product_name()` - 获取需求所属产品名称
- `submit_testcase()` - 提交测试用例（POST 请求）
- `submit_bug_report()` - 提交缺陷报告（POST 请求）

### utils/file_utils.py
通用工具函数模块。

**提供功能：**
- `read_json_file()` - 安全读取 JSON 文件
- `read_txt_file()` - 读取文本文件
- `extract_text_from_story_folders()` - 从需求文件夹提取文本
- 文件相关的辅助工具函数

### workflow/workflow_manager.py
工作流管理器，负责协调各个阶段的执行顺序。

**核心功能：**
- `run_full_pipeline()` - 运行完整流程
- `run_stage()` - 运行单个阶段
- `clean_files()` - 清理各阶段文件

### workflow/state_manager.py
状态管理器，记录运行状态和断点信息。

**核心功能：**
- `create_new_run()` - 创建新的运行记录
- `update_stage_status()` - 更新阶段状态
- `get_completed_stories()` - 获取已完成的需求列表
- `record_error()` - 记录错误信息

### workflow/download_stage.py
下载阶段处理，负责从禅道系统下载需求文件。

### workflow/gpt_stage.py
GPT处理阶段，利用AI生成测试用例。

**核心改进：**
- 支持根据 `story_ids` 过滤处理的文件
- 并行处理多个文件

### workflow/process_stage.py
处理阶段，对下载的数据进行处理和转换。

### workflow/submit_stage.py
提交阶段，将处理后的数据提交到禅道系统。

## 依赖技术

| 技术 | 用途 |
|------|------|
| **Python 3.x** | 编程语言 |
| **Selenium WebDriver** | 浏览器自动化（登录、文件下载） |
| **requests** | HTTP 请求（表单提交） |
| **Win32 API** | Windows 系统交互 |
| **JSON** | 数据解析 |
| **python-docx/python-pptx** | 文档处理 |

## 工作流程

```
下载阶段 → 处理阶段 → GPT阶段 → 提交阶段
    ↓           ↓          ↓          ↓
  登录一次   提取文本   生成用例    提交数据
  (共享会话)              ↓
                    按需求过滤
```

## 核心改进

1. **登录优化**：整个流程只需登录一次，下载和提交阶段共享会话
2. **提交优化**：使用 requests 替代 Selenium 进行表单提交，速度更快
3. **浏览器优化**：启动时自动最小化，不干扰当前工作
4. **调试模式**：可预览提交内容而不实际提交
5. **状态管理**：支持断点续跑，记录运行状态

## 用途

本项目用于自动化提交测试用例和缺陷报告到禅道（ZenTao）项目管理系统，减少人工操作工作量，提高工作效率。