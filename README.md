# auto_submit_zentao

禅道自动化提交工具 - 自动化提交测试用例和缺陷报告到禅道项目管理系统

## 功能特性

- 自动化登录禅道系统（使用 Selenium 登录，避免密码修改重定向问题）
- 批量提交测试用例（使用 requests 直接发送 POST 请求，更快速高效）
- 自动生成并提交缺陷报告
- 支持工作流管理，包含下载、处理、GPT生成、提交等阶段
- 整个流程只需登录一次，复用会话
- 浏览器启动时自动最小化，不干扰当前工作
- 支持调试模式，可预览提交内容而不实际提交
- 减少人工操作工作量，提高工作效率

## 技术栈

- **Python 3.x** - 编程语言
- **Selenium WebDriver** - 浏览器自动化（用于登录和文件下载）
- **requests** - HTTP 请求库（用于表单提交，替代 Selenium）
- **Win32 API** - Windows 系统交互
- **JSON** - 数据解析

## 项目结构

```
auto_submit_zentao/
├── config/          # 配置模块
│   └── constants.py # 常量定义与配置
├── core/            # 核心业务模块
│   ├── business_handler.py  # 业务处理逻辑
│   ├── page_operations.py   # 页面操作封装（Selenium）
│   └── api_submitter.py     # API提交器（requests）
├── utils/           # 工具模块
│   └── file_utils.py        # 文件操作工具函数
├── workflow/        # 工作流模块
│   ├── download_stage.py    # 下载阶段处理
│   ├── gpt_stage.py         # GPT处理阶段
│   ├── process_stage.py     # 处理阶段
│   ├── submit_stage.py      # 提交阶段
│   ├── workflow_manager.py  # 工作流管理器
│   └── state_manager.py     # 状态管理器
├── main.py          # 程序主入口
├── PROJECT_STRUCTURE.md  # 项目结构详细说明
└── README.md        # 项目说明文档
```

## 安装步骤

1. 克隆项目到本地
2. 安装依赖包：
   ```bash
   pip install selenium requests pywin32 python-dotenv python-pptx python-docx
   ```
3. 配置 Edge 浏览器驱动（确保已安装 Microsoft Edge 浏览器）

## 配置说明

### 方式一：使用环境变量（推荐）

1. 复制 `.env.example` 文件为 `.env`：
   ```bash
   copy .env.example .env
   ```

2. 编辑 `.env` 文件，填写您的敏感配置：
   ```ini
   # 禅道登录配置
   ZENTAO_USERNAME=your_username
   ZENTAO_PASSWORD=your_password

   # 禅道服务器地址
   ZENTAO_BASE_URL=http://your_zentao_server:port

   # GPT API 配置
   GPT_API_KEY=your_api_key_here
   GPT_API_URL=https://api.deepseek.com/v1/chat/completions
   GPT_MODEL=deepseek-chat

   # 路径配置（可选）
   DRIVER_PATH=C:\path\to\msedgedriver.exe
   DOWNLOAD_FOLDER=D:\VayoPro\需求方案\down
   OUTPUT_BASE_FOLDER=D:\VayoPro\需求方案\mid
   JSON_DATA_PATH=D:\VayoPro\需求方案\gpt_output\
   ```

### 方式二：修改配置文件

在 `config/constants.py` 中配置以下内容：

- `USERNAME` - 登录用户名
- `PASSWORD` - 登录密码
- `ZENTAO_BASE_URL` - 禅道服务器地址
- `GPT_API_KEY` - GPT API 密钥
- `DRIVER_PATH` - Edge 浏览器驱动路径
- `DOWNLOAD_FOLDER` - 下载文件夹路径
- `OUTPUT_BASE_FOLDER` - 输出基础文件夹路径
- `JSON_DATA_PATH` - JSON数据文件夹路径
- `PRODUCT_DICT` - 产品ID映射字典
- `DEBUG_MODE` - 调试模式（True 时不实际提交）
- `DEFAULT_STORY_ID_LIST` - 默认需求ID列表

> **安全提示**：推荐使用环境变量方式配置敏感信息，避免将密码和API密钥提交到版本控制系统。

## 使用方法

### 运行完整流程

```bash
python main.py run
```

### 运行单个阶段

```bash
# 仅下载
python main.py download

# 仅处理
python main.py process

# 仅GPT生成
python main.py gpt

# 仅提交
python main.py submit
```

### 指定需求ID

```bash
python main.py run --story-ids 3807 3808 3809
```

### 跳过已完成的需求

```bash
python main.py run --no-skip  # 不跳过已完成的需求，重新执行所有阶段
```

### 断点续跑

```bash
python main.py run --resume  # 从上次失败的阶段继续执行
```

## 工作流阶段说明

| 阶段 | 名称 | 说明 |
|------|------|------|
| 1 | download | 从禅道下载需求文件（使用 Selenium） |
| 2 | process | 处理下载的需求文件，提取文本内容 |
| 3 | gpt | 调用 GPT 生成测试用例 |
| 4 | submit | 提交测试用例到禅道（使用 requests） |

## 核心模块说明

| 文件 | 说明 |
|------|------|
| **main.py** | 程序主入口，解析命令行参数并启动工作流 |
| **config/constants.py** | 系统常量与配置定义 |
| **core/business_handler.py** | 核心业务处理模块，协调登录和提交操作 |
| **core/page_operations.py** | 页面操作封装类（Selenium，用于登录和下载） |
| **core/api_submitter.py** | API提交器（requests，用于表单提交） |
| **utils/file_utils.py** | 通用工具函数模块 |
| **workflow/workflow_manager.py** | 工作流管理器，编排各阶段执行 |
| **workflow/state_manager.py** | 状态管理器，记录运行状态和断点信息 |

## 调试模式

设置 `DEBUG_MODE = True` 时：
- 所有表单提交操作将仅输出日志，不实际提交到禅道
- 适合测试和验证流程

## 注意事项

1. **浏览器窗口**：浏览器启动时会自动最小化，不会干扰当前工作
2. **登录会话**：整个流程只需登录一次，下载阶段和提交阶段共享会话
3. **文件权限**：确保配置的下载和输出文件夹有写入权限
4. **网络环境**：确保能访问禅道服务器和 GPT API

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License