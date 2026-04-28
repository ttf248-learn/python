- 生成中文版本的 git 提交记录，消息遵循 conventionalcommits 规范，包含清晰的变更说明和详细的文件修改列表

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a multi-functional Python project containing data analysis, automation scripts, OCR image processing, file management tools, and Jupyter notebooks. The project is organized into modular scripts and interactive notebooks for various use cases.

## Repository Structure

```
├── assets/                    # Static resources
│   ├── fonts/                # Font files (e.g., simfang.ttf for PaddleOCR)
│   └── images/               # Image resources
├── notebooks/                # Jupyter Notebooks
│   ├── data_analysis.ipynb   # Data analysis examples
│   ├── market_indicators.ipynb
│   ├── python_syntax_sugar.ipynb
│   ├── yinktech_dev.ipynb
│   └── yfinance/            # Financial data analysis with yfinance
├── output/                  # Generated output files
├── scripts/                 # Main scripts directory (organized by category)
│   ├── automation/          # Automation scripts
│   │   └── palworld_helper.py    # Game automation (Palworld)
│   ├── data_analysis/       # Financial and market data analysis
│   │   └── easymoney.py     # Technical indicators &东方财富 API integration
│   ├── file_management/     # File and folder utilities
│   │   ├── folder_monitor.py     # Monitors folder size changes
│   │   ├── organize_files_by_year.py
│   │   ├── rename_images.py
│   │   └── requirements.txt      # File management dependencies
│   └── image_processing/    # Image processing tools
│       ├── paddle_ocr/      # OCR functionality with PaddleOCR
│       ├── pic_to_gray.py   # Image color conversion
│       ├── svg_to_png.py    # SVG to PNG conversion
│       └── svg_to_png_inkscape.py
└── .github/
    └── prompts/
        └── python.prompt.md      # GitHub Copilot prompts (Chinese)
```

## Development Workflow

### Running Scripts

Each script is self-contained and can be run directly:

```bash
# File monitoring
python scripts/file_management/folder_monitor.py "/path/to/folder" -i 1.0

# OCR processing
python scripts/image_processing/paddle_ocr/ocr_save_image.py

# Financial data analysis
python scripts/data_analysis/easymoney.py

# Game automation (Palworld)
python scripts/automation/palworld_helper.py
```

### Running Jupyter Notebooks

```bash
cd notebooks
jupyter notebook
# or
jupyter lab
```

### Dependencies

Dependencies are managed per-module rather than at the project root:

- **File Management**: `scripts/file_management/requirements.txt`
  - colorama==0.4.6
  - loguru==0.7.3
  - win32_setctime==1.2.0

- **Image Processing (OCR)**: PaddleOCR and related dependencies (install via pip)
  - `pip install paddleocr`
  - `pip install paddlepaddle` (for CPU) or `paddlepaddle-gpu` (for GPU)

- **Data Analysis**: Standard data science stack
  - pandas, numpy, requests, scipy

Install module-specific dependencies:
```bash
pip install -r scripts/file_management/requirements.txt
pip install paddleocr paddlepaddle  # For OCR functionality
```

## Key Features by Category

### 1. File Management (`scripts/file_management/`)

- **folder_monitor.py**: Real-time folder size monitoring with growth statistics
  - Uses `loguru` for logging (daily rotation, 30-day retention)
  - Tracks size changes at multiple intervals (minute, hour, 12-hour, day)
  - Outputs to both console and log files in `log/` directory
  - Command-line interface with configurable intervals

- **organize_files_by_year.py**: Organizes files by year
- **rename_images.py**: Batch image renaming utility

### 2. Data Analysis (`scripts/data_analysis/`, `notebooks/`)

- **easymoney.py**: Financial data analysis with technical indicators
  - Integrates with 东方财富 (East Money) API for K-line data
  - Calculates 16+ technical indicators (MA, EMA, Ichimoku Cloud, etc.)
  - Exports to CSV, uses SQLite for storage

- **notebooks/yfinance/**: Financial data analysis using yfinance library
- Multiple Jupyter notebooks for interactive data exploration

### 3. Image Processing (`scripts/image_processing/`)

- **paddle_ocr/**: OCR text recognition
  - Supports multiple languages (Chinese, English, etc.)
  - Visualizes OCR results with bounding boxes
  - Requires fonts in `assets/fonts/` (simfang.ttf for Chinese)

- **Image conversion tools**:
  - `pic_to_gray.py`: Convert images to grayscale
  - `svg_to_png.py` & `svg_to_png_inkscape.py`: SVG to PNG conversion

### 4. Automation (`scripts/automation/`)

- **palworld_helper.py**: Game automation for Palworld
  - Uses `keyboard` and `pyautogui` for input simulation
  - Automates repetitive in-game actions (egg hatching process)
  - Hotkey-driven (press 'n' to start automation)

## Logging Configuration

The project uses **loguru** for logging (not standard logging):
- Logs are written to `log/` directory with daily rotation
- 30-day log retention policy
- Format: `{time:YYYY-MM-DD HH:mm:ss} - {level} - {name}:{function}:{line} - {message}`

Example from `folder_monitor.py:40-41`:
```python
logger.add(log_file_path, rotation="00:00", retention="30 days", level="DEBUG", format=log_format)
```

## Important Implementation Notes

1. **No Central Requirements**: Each module may have its own `requirements.txt`. Check `scripts/file_management/requirements.txt` for example.

2. **Logging Standard**: Uses `loguru` library instead of Python's standard `logging`. All new scripts should follow this pattern.

3. **Path Handling**: Scripts use `pathlib.Path` for cross-platform compatibility.

4. **API Integration**:
   - 东方财富 API for financial data (easymoney.py:27)
   - PaddleOCR for text recognition

5. **GitHub Copilot**: Chinese-language prompts are configured in `.github/prompts/python.prompt.md` - follow these guidelines when generating code.

6. **Development Environment**:
   - VS Code configuration in `.vscode/`
   - Virtual environment recommendations (`.venv` in notebooks/)
   - Git-based workflow with frequent refactoring commits

## Common Development Tasks

### Adding a New Script

1. Create in appropriate category under `scripts/`
2. Use `loguru` for logging (follow pattern in existing scripts)
3. Add module-specific `requirements.txt` if needed
4. Include command-line argument parsing
5. Follow PEP 8 style guidelines

### Working with Financial Data

- 港股回购分析使用东方财富回购页和报价页实时接口，不依赖历史 K 线接口
- 东方财富报价页实时接口: `https://push2.eastmoney.com/api/qt/stock/get`
- Technical indicators use pandas, numpy, scipy

### Working with OCR

- PaddleOCR initialization: `PaddleOCR(use_angle_cls=True, lang="ch")`
- Required font files in `assets/fonts/`
- Image paths use project-relative references via `os.path.join(project_root, ...)`

## Security & Configuration

- **Ignored files**: Log files (`.log`), virtual environments (`.venv`), encrypted config files
- **Sensitive data**: Email configs and encryption keys stored in `scripts/config/` (encrypted)
- **No CI/CD**: No automated testing or build pipelines detected

## Recent Changes (from git history)

- Migrated from standard `logging` to `loguru` for improved logging
- Modularized scripts into category folders
- Simplified folder_monitor by removing JSON output options
- Added file management dependencies

## Environment Notes

- Platform: Linux (kernel 6.8.0-87-generic)
- Python 3.8+ required
- Some scripts may have Windows-specific dependencies (e.g., `win32_setctime` in file management)
