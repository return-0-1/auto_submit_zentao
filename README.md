# auto_submit_zentao

禅道自动化提交工具 - 自动化提交测试用例和缺陷报告到禅道项目管理系统

## 功能特性

- 自动化登录禅道系统
- 批量提交测试用例
- 自动生成并提交缺陷报告
- 支持工作流管理，包含下载、处理、GPT生成、提交等阶段
- 减少人工操作工作量，提高工作效率

## 技术栈

- **Python 3.x** - 编程语言
- **Selenium WebDriver** - 浏览器自动化
- **Win32 API** - Windows 系统交互
- **JSON** - 数据解析

## 项目结构

```
auto_submit_zentao/
├── config/          # 配置模块
│   └── constants.py # 常量定义与配置
├── core/            # 核心业务模块
│   ├── business_handler.py  # 业务处理逻辑
│   └── page_operations.py   # 页面操作封装
├── utils/           # 工具模块
│   └── file_utils.py        # 文件操作工具函数
├── workflow/        # 工作流模块
│   ├── download_stage.py    # 下载阶段处理
│   ├── gpt_stage.py         # GPT处理阶段
│   ├── process_stage.py     # 处理阶段
│   ├── submit_stage.py      # 提交阶段
│   └── workflow_manager.py  # 工作流管理器
├── main.py          # 程序主入口
├── PROJECT_STRUCTURE.md  # 项目结构详细说明
└── README.md        # 项目说明文档
```

## 安装步骤

1. 克隆项目到本地
2. 安装依赖包：
   ```bash
   pip install selenium pywin32 python-dotenv python-pptx python-docx
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

   # GPT API 配置
   GPT_API_KEY=your_api_key_here

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
- `GPT_API_KEY` - GPT API 密钥
- `DRIVER_PATH` - Edge 浏览器驱动路径
- `DOWNLOAD_FOLDER` - 下载文件夹路径
- `OUTPUT_BASE_FOLDER` - 输出基础文件夹路径
- `JSON_DATA_PATH` - JSON数据文件夹路径
- `PRODUCT_DICT` - 产品ID映射字典

> **安全提示**：推荐使用环境变量方式配置敏感信息，避免将密码和API密钥提交到版本控制系统。

## 使用方法

```bash
python main.py
```

## 文件说明

- **main.py** - 程序主入口，初始化工作流管理器并启动自动化流程
- **config/constants.py** - 系统常量与配置定义
- **core/business_handler.py** - 核心业务处理模块
- **core/page_operations.py** - 页面操作封装类
- **utils/file_utils.py** - 通用工具函数模块
- **workflow/workflow_manager.py** - 工作流管理器

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License