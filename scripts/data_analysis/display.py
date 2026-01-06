"""
This module handles the presentation logic for the stock buyback data.
It uses the 'rich' library to create beautifully formatted tables and summaries in the console.
"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.box import ROUNDED

console = Console()

def format_currency(value):
    """Formats a number as a currency string with commas."""
    if value is None:
        return "N/A"
    return f"{value:,.2f}"

def format_quantity(value):
    """Formats a number as a quantity string with commas."""
    if value is None:
        return "N/A"
    return f"{value:,.0f}"

def print_summary(df, stock_code, period, summary_df, total_amount, total_quantity, total_avg_price):
    """
    Displays a rich summary including period-based aggregation and a grand total panel.
    """
    period_str = '年度' if period == 'year' else '月度'
    table = Table(
        title=f"[bold cyan]股票代码 {stock_code} - {period_str}回购汇总[/bold cyan]",
        box=ROUNDED,
        header_style="bold magenta"
    )

    table.add_column("周期", justify="center", style="cyan", no_wrap=True)
    table.add_column("回购总额 (港元)", justify="right", style="green")
    table.add_column("回购数量 (股)", justify="right", style="yellow")
    table.add_column("加权均价", justify="right", style="red")

    for index, row in summary_df.iterrows():
        table.add_row(
            str(index),
            format_currency(row['TotalAmount']),
            format_quantity(row['TotalQuantity']),
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
        ("总回购次数: ", "default"),
        (f"{total_buyback_days} 天\n", "bold blue"),
        ("日均回购额: ", "default"),
        (f"{format_currency(avg_daily_amount)} 港元", "bold magenta"),
    )

    summary_panel = Panel(
        summary_text,
        title="[bold]全局统计摘要[/bold]",
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
