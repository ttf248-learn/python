# Python 学习与工具项目

这是一个用于学习 Python 和开发实用工具的项目。

## 项目结构

```bash
├── assets/             # 资源文件目录
│   ├── fonts/         # 字体文件
│   └── images/        # 图片资源
├── notebooks/         # Jupyter notebooks
│   ├── data_analysis.ipynb    # 数据分析示例
│   ├── market_indicators.ipynb # 市场指标计算
│   ├── python_syntax_sugar.ipynb # Python 语法糖学习
│   └── yinktech_dev.ipynb    # 业务开发相关
├── output/            # 输出文件目录
├── scripts/           # 实用工具脚本
│   ├── config/       # 配置文件目录
│   ├── paddle_ocr/   # OCR 文字识别工具
│   └── *.py          # 其他工具脚本
└── requirements.txt   # 项目依赖
```

## 功能模块

### 1. 数据分析工具

- NumPy 和 Pandas 基础操作示例
- 市场技术指标计算（MA、EMA 等）
- 数据可视化

### 2. OCR 文字识别

- 基于 PaddleOCR 的中文文字识别
- 支持图片文字识别并保存结果
- 详细使用说明见 [scripts/paddle_ocr/Readme.md](scripts/paddle_ocr/Readme.md)

### 3. 邮件发送工具

- 支持加密配置管理
- 基于 SMTP 的邮件发送功能
- 使用 Fernet 加密存储敏感信息

## 环境配置

### 创建虚拟环境

```bash
python -m venv .venv
```

### 激活虚拟环境

```bash
# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate
```

### 安装依赖

```bash
pip install -r requirements.txt
```

## 特别说明

### OCR 模型文件存储位置

- Windows: C:\Users\{username}\.paddleocr
- Linux/macOS: ${HOME}/.paddleocr

### 邮件配置

- 首次使用需运行 `scripts/create_config.py` 创建配置
- 配置文件位于 `scripts/config/` 目录
- 请确保 `.gitignore` 中包含敏感配置文件
