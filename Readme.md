# 项目概述

本项目是一个多功能的 Python 项目，包含数据分析、自动化脚本、OCR 图像处理等功能，适用于多种场景。

## 项目结构

```plaintext
├── assets/                # 静态资源文件夹
│   ├── fonts/            # 字体文件
│   └── images/           # 图片资源
├── notebooks/            # Jupyter Notebook 文件
│   ├── data_analysis.ipynb
│   ├── market_indicators.ipynb
│   ├── python_syntax_sugar.ipynb
│   ├── yinktech_dev.ipynb
│   └── yfinance/         # 财务数据分析
├── output/               # 输出结果
├── scripts/              # 脚本文件
│   ├── create_config.py  # 配置文件生成脚本
│   ├── easymoney.py      # 财务相关脚本
│   ├── paddle_ocr/       # OCR 相关脚本
├── requirements.txt      # 项目依赖
└── Readme.md             # 项目说明文件
```

## 功能模块

### 1. 数据分析

- **notebooks/data_analysis.ipynb**: 数据分析的 Jupyter Notebook。
- **notebooks/yfinance/**: 使用 yfinance 进行财务数据分析。

### 2. 自动化脚本

- **scripts/create_config.py**: 自动生成配置文件，支持加密密钥的生成。
- **scripts/easymoney.py**: 财务数据处理脚本。

### 3. OCR 图像处理

- **scripts/paddle_ocr/**: 使用 PaddleOCR 进行图像文字识别。

## 安装依赖

请确保已安装 Python 3.8 或更高版本。然后运行以下命令安装依赖：

```bash
pip install -r requirements.txt
```

## 使用方法

### 运行 Jupyter Notebook

进入 `notebooks` 文件夹，运行以下命令启动 Jupyter Notebook：

```bash
jupyter notebook
```

### 运行脚本

以 `create_config.py` 为例，运行以下命令：

```bash
python scripts/create_config.py
```

## 贡献

欢迎提交 Issue 或 Pull Request 来改进本项目。

## 许可证

本项目采用 MIT 许可证。
