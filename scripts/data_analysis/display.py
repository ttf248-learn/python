"""
This module handles the presentation logic for the stock buyback data.
It uses the 'rich' library to create beautifully formatted tables and summaries in the console.
"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.box import ROUNDED
import pandas as pd

console = Console()

def format_currency(value):
    """Formats a number as a currency string with commas."""
    if value is None or pd.isna(value):
        return "N/A"
    return f"{value:,.2f}"


def format_compact_currency(value):
    """Formats large HKD values compactly for analysis tables."""
    if value is None or pd.isna(value):
        return "N/A"
    if abs(value) >= 100000000:
        return f"{value / 100000000:.2f}亿"
    if abs(value) >= 10000:
        return f"{value / 10000:.2f}万"
    return f"{value:.2f}"

def format_quantity(value):
    """Formats a number as a quantity string with commas."""
    if value is None or pd.isna(value):
        return "N/A"
    return f"{value:,.0f}"

def format_change(value):
    """Formats a percentage change with color."""
    if value is None or pd.isna(value):
        return "[dim]N/A[/dim]"
    
    color = "green" if value > 0 else "red"
    return f"[{color}]{value:+.2f}%[/{color}]"


def format_percent(value):
    """Formats a percentage value."""
    if value is None or pd.isna(value):
        return "N/A"
    return f"{value:.2f}%"


def format_price(value):
    """Formats a stock price."""
    if value is None or pd.isna(value):
        return "N/A"
    return f"{value:.3f}"


def _snapshot_value(snapshot, column):
    if snapshot is None or column not in snapshot:
        return None
    value = snapshot[column]
    if pd.isna(value):
        return None
    return value


def print_summary(
    df,
    stock_code,
    period,
    summary_df,
    total_amount,
    total_quantity,
    total_avg_price,
    target_date=None,
    period_label=None,
):
    """
    Displays a rich summary including period-based aggregation and a grand total panel.
    """
    if period == 'year':
        period_str = '年度'
        panel_title = '[bold]当前统计摘要[/bold]'
    elif period == 'month':
        period_str = '月度'
        panel_title = '[bold]当前统计摘要[/bold]'
    else:
        period_str = period_label or (target_date.strftime('%Y-%m-%d') if target_date else '指定日期')
        panel_title = f"[bold]{period_str} 统计摘要[/bold]"
    table = Table(
        title=f"[bold cyan]股票代码 {stock_code} - {period_str}回购汇总[/bold cyan]",
        box=ROUNDED,
        header_style="bold magenta"
    )

    table.add_column("周期", justify="center", style="cyan", no_wrap=True)
    table.add_column("回购总额 (港元)", justify="right", style="green")
    table.add_column("同比/环比变化", justify="right")
    table.add_column("回购天数", justify="center", style="blue")
    table.add_column("日均回购额", justify="right", style="magenta")
    table.add_column("加权均价", justify="right", style="red")

    # The dataframe is sorted descending, so we iterate in reverse to show oldest first
    for index, row in summary_df.iloc[::-1].iterrows():
        table.add_row(
            str(index),
            format_currency(row['TotalAmount']),
            format_change(row['PoP_Change']),
            str(row['BuybackDays']),
            format_currency(row['AvgDailyAmount']),
            f"{row['WeightedAvgPrice']:.3f}"
        )

    console.print(table)

    # --- Grand Total Panel ---
    total_buyback_days = len(df['日期'].unique())
    avg_daily_amount = total_amount / total_buyback_days if total_buyback_days else 0

    summary_text = Text.assemble(
        ("总回购额: ", "default"),
        (f"{format_currency(total_amount)} 港元\n", "bold green"),
        ("总回购量: ", "default"),
        (f"{format_quantity(total_quantity)} 股\n", "bold yellow"),
        ("总加权均价: ", "default"),
        (f"{total_avg_price:.3f}\n", "bold red"),
        ("总回购天数: ", "default"),
        (f"{total_buyback_days} 天\n", "bold blue"),
        ("日均回购额: ", "default"),
        (f"{format_currency(avg_daily_amount)} 港元", "bold magenta"),
    )

    summary_panel = Panel(
        summary_text,
        title=panel_title,
        border_style="blue",
        expand=False
    )
    console.print(summary_panel)


def print_data_view(df, stock_code, limit):
    """
    Displays the raw buyback data in a nicely formatted table.
    """
    if df.empty:
        console.print(f"[yellow]No data found for stock {stock_code}.[/yellow]")
        return

    table = Table(
        title=f"[bold cyan]股票代码 {stock_code} - 最近 {limit} 条回购记录[/bold cyan]",
        box=ROUNDED,
        header_style="bold magenta"
    )

    # Define columns
    table.add_column("日期", justify="center", style="cyan")
    table.add_column("回购总额 (港元)", justify="right", style="green")
    table.add_column("回购数量 (股)", justify="right", style="yellow")
    table.add_column("回购平均价", justify="right", style="red")
    table.add_column("最高价", justify="right", style="blue")
    table.add_column("最低价", justify="right", style="purple")

    # Add rows from DataFrame
    for _, row in df.head(limit).iterrows():
        table.add_row(
            str(row['日期'].date()),
            format_currency(row['回购总额(港元)']),
            format_quantity(row['回购数量(股)']),
            f"{row['回购平均价']:.3f}",
            f"{row['最高回购价']:.3f}",
            f"{row['最低回购价']:.3f}"
        )

    console.print(table)


def print_analysis_report(report):
    """
    Displays a trading-oriented buyback analysis report.
    """
    if not report.get("signal"):
        for warning in report.get("warnings", []):
            console.print(f"[yellow]{warning}[/yellow]")
        return

    stock_code = report["stock_code"]
    stock_name = report.get("stock_name") or ""
    latest_date = report.get("latest_date")
    signal = report["signal"]
    signal_color = {
        "偏积极": "green",
        "观察": "yellow",
        "偏谨慎": "red",
    }.get(signal["label"], "white")

    title = f"{stock_code} {stock_name}".strip()
    latest_date_text = latest_date.strftime("%Y-%m-%d") if latest_date is not None else "N/A"
    reason_text = "\n".join(f"- {reason}" for reason in signal.get("reasons", [])) or "- 暂无明确触发项"

    overview_text = Text.assemble(
        ("信号: ", "default"),
        (signal["label"], f"bold {signal_color}"),
        (f"  (score {signal['score']})\n", "dim"),
        ("最新日期: ", "default"),
        (f"{latest_date_text}\n", "bold cyan"),
        ("当前价: ", "default"),
        (f"{format_price(signal.get('current_price'))}\n", "bold"),
        ("近30天加速: ", "default"),
        (f"{format_percent(signal.get('acceleration_30'))}\n", "bold"),
        ("当前价相对近期回购均价: ", "default"),
        (f"{format_percent(signal.get('close_vs_buyback_price'))}\n\n", "bold"),
        ("核心原因:\n", "bold"),
        (reason_text, "default"),
    )
    console.print(
        Panel(
            overview_text,
            title=f"[bold cyan]{title} 回购分析助手[/bold cyan]",
            border_style=signal_color,
            expand=False,
        )
    )

    _print_basic_snapshot(report.get("basic_snapshot"))
    _print_window_metrics(report.get("window_metrics"))
    _print_period_table(report.get("monthly_summary"), "月度回购趋势", max_rows=12)
    _print_period_table(report.get("yearly_summary"), "年度回购汇总", max_rows=5)

    warnings = report.get("warnings") or []
    if warnings:
        warning_text = "\n".join(f"- {warning}" for warning in warnings)
        console.print(Panel(warning_text, title="[bold yellow]数据提示[/bold yellow]", border_style="yellow", expand=False))

    console.print(
        "[dim]提示: 回购只能反映公司资金动作和价格态度，不能单独作为买卖依据；请结合基本面、市场环境和仓位管理。[/dim]"
    )


def _print_window_metrics(df):
    if df is None or df.empty:
        return

    table = Table(title="[bold cyan]近端回购强度[/bold cyan]", box=ROUNDED, header_style="bold magenta")
    table.add_column("窗口", justify="center", style="cyan")
    table.add_column("回购总额", justify="right", style="green")
    table.add_column("回购天数", justify="center", style="blue")
    table.add_column("加权均价", justify="right", style="red")

    for _, row in df.iterrows():
        table.add_row(
            str(row["窗口"]),
            format_compact_currency(row["回购总额"]),
            str(int(row["回购天数"])),
            format_price(row["加权均价"]),
        )
    console.print(table)


def _print_basic_snapshot(snapshot):
    if snapshot is None:
        return

    table = Table(title="[bold cyan]当前基础数据[/bold cyan]", box=ROUNDED, header_style="bold magenta")
    table.add_column("字段", justify="center", style="cyan")
    table.add_column("数值", justify="right")
    rows = [
        ("当前价", format_price(_snapshot_value(snapshot, "最新价"))),
        ("今开", format_price(_snapshot_value(snapshot, "今开"))),
        ("最高/最低", f"{format_price(_snapshot_value(snapshot, '最高'))} / {format_price(_snapshot_value(snapshot, '最低'))}"),
        ("涨跌幅", format_percent(_snapshot_value(snapshot, "涨跌幅"))),
        ("成交量", format_quantity(_snapshot_value(snapshot, "成交量"))),
        ("成交额", format_compact_currency(_snapshot_value(snapshot, "成交额"))),
        ("总市值", format_compact_currency(_snapshot_value(snapshot, "总市值"))),
        ("港市值", format_compact_currency(_snapshot_value(snapshot, "港市值"))),
        ("市净率", format_price(_snapshot_value(snapshot, "市净率"))),
        ("换手率", format_percent(_snapshot_value(snapshot, "换手率"))),
        (
            "52周区间",
            f"{format_price(_snapshot_value(snapshot, '52周最低'))} - {format_price(_snapshot_value(snapshot, '52周最高'))}",
        ),
    ]
    for label, value in rows:
        table.add_row(label, value)
    console.print(table)


def _print_period_table(df, title, max_rows):
    if df is None or df.empty:
        return

    table = Table(title=f"[bold cyan]{title}[/bold cyan]", box=ROUNDED, header_style="bold magenta")
    table.add_column("周期", justify="center", style="cyan")
    table.add_column("回购总额", justify="right", style="green")
    table.add_column("同比/环比", justify="right")
    table.add_column("回购天数", justify="center", style="blue")
    table.add_column("日均回购额", justify="right", style="magenta")
    table.add_column("加权均价", justify="right", style="red")

    for _, row in df.tail(max_rows).iterrows():
        table.add_row(
            str(row["周期"]),
            format_compact_currency(row["回购总额"]),
            format_change(row["同比环比变化"]),
            str(int(row["回购天数"])),
            format_compact_currency(row["日均回购额"]),
            format_price(row["加权均价"]),
        )
    console.print(table)
