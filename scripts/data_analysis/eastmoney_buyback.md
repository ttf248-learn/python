# 东方财富港股回购脚本

用于抓取、查看和汇总港股回购数据，本地数据保存在 `scripts/data_analysis/data/`。

## 安装

```bash
pip install -r scripts/data_analysis/requirements.txt
```

## 用法

### `fetch`

抓取并更新指定股票的回购数据。

```bash
python scripts/data_analysis/eastmoney_buyback.py fetch <stock_code>
```

示例：

```bash
python scripts/data_analysis/eastmoney_buyback.py fetch 00700
```

### `view`

查看本地最近的回购记录。

```bash
python scripts/data_analysis/eastmoney_buyback.py view <stock_code> [--limit 10]
```

示例：

```bash
python scripts/data_analysis/eastmoney_buyback.py view 01810
python scripts/data_analysis/eastmoney_buyback.py view 01810 --limit 25
```

### `summary`

按年、月汇总，或按“指定日期到最新数据”汇总回购数据。

```bash
python scripts/data_analysis/eastmoney_buyback.py summary <stock_code> <year|month|date> [YYYY-MM-DD]
```

`date` 模式表示从 `YYYY-MM-DD` 当天开始，一直到最新数据的汇总。

示例：

```bash
python scripts/data_analysis/eastmoney_buyback.py summary 00700 year
python scripts/data_analysis/eastmoney_buyback.py summary 01810 month
python scripts/data_analysis/eastmoney_buyback.py summary 00700 date 2026-01-15
```
