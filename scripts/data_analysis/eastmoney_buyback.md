# 东方财富港股回购分析助手

用于抓取、查看、汇总和分析港股回购数据。本地数据保存在 `scripts/data_analysis/data/`，回购数据来自东方财富港股回购页，基础行情数据来自东方财富港股报价页的实时接口快照。

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

### `analyze`

输入港股代码后，更新回购缓存和当日基础行情快照，并输出中短线交易辅助报告。默认分析近 1 年数据。

```bash
python scripts/data_analysis/eastmoney_buyback.py analyze <stock_code> [--window 1y|3y|all] [--no-update] [--export]
```

报告包含：

- 当前辅助信号：`偏积极`、`观察`、`偏谨慎`
- 近 7 / 30 / 90 天回购强度
- 当前价相对近期回购均价的位置
- 成交额、总市值、港市值、市净率、换手率、52周价格区间
- 月度和年度回购趋势

基础行情说明：

- 先访问 `https://quote.eastmoney.com/hk/<stock_code>.html`，再使用页面实时接口 `https://push2.eastmoney.com/api/qt/stock/get` 获取当前基础数据。
- 本地快照保存为 `scripts/data_analysis/data/basics_<stock_code>.csv`，同一天重复运行会更新当天行，不新增重复日期。
- 基础字段包含日期、股票代码、股票名称、最新价、今开、最高、最低、昨收、涨跌额、涨跌幅、成交量、成交额、总市值、港市值、市净率、换手率、52周最高、52周最低、数据源。

示例：

```bash
python scripts/data_analysis/eastmoney_buyback.py analyze 01810
python scripts/data_analysis/eastmoney_buyback.py analyze 00700 --window 1y
python scripts/data_analysis/eastmoney_buyback.py analyze 01810 --no-update
python scripts/data_analysis/eastmoney_buyback.py analyze 01810 --export
```

## 打包 EXE

打包脚本位于 `scripts/data_analysis/build_exe.ps1`。推荐在项目根目录执行：

```powershell
.\scripts\data_analysis\build_exe.ps1
```

脚本内部会自动切换到项目根目录后再调用 PyInstaller，所以从其他目录执行脚本也能使用相同的相对路径。生成结果：

- `dist/eastmoney_buyback_01810.exe`
- `dist/data/`：exe 运行时的回购和基础行情缓存目录

这个 exe 无参数启动时默认执行：

```powershell
python scripts/data_analysis/eastmoney_buyback.py analyze 01810
```

双击运行后会在报告结尾停留，显示 `Press Enter to exit...`，按回车退出。

注意：回购数据只能反映公司资金动作和价格态度，不能单独作为买卖依据。报告用于辅助判断，需要结合基本面、市场环境和仓位管理。
