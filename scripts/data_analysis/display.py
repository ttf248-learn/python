"""
This module handles the presentation logic for the stock buyback data.
It uses the 'rich' library to create beautifully formatted tables and summaries in the console.
"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.box import ROUNDED, SIMPLE
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


def format_signed_percent(value):
    """Formats a signed percentage with color."""
    if value is None or pd.isna(value):
        return "[dim]N/A[/dim]"
    color = "green" if value <= 0 else "yellow" if value <= 15 else "red"
    return f"[{color}]{value:+.2f}%[/{color}]"


def _snapshot_value(snapshot, column):
    if snapshot is None or column not in snapshot:
        return None
    value = snapshot[column]
    if pd.isna(value):
        return None
    return value


def _compact_reason(reason):
    replacements = {
        "近30天仍有回购": "30天有回购",
        "近30天未观察到回购": "30天无回购",
        "近30天回购较前30天明显加速": "明显加速",
        "近30天回购较前30天温和加速": "温和加速",
        "近30天回购较前30天明显减速": "明显减速",
        "近30天回购较前30天有所减速": "有所减速",
        "最近一周内有回购记录": "一周内回购",
        "最近一次回购距离当前超过30天": "超30天未回购",
        "最近一次回购距离当前超过两周": "超两周未回购",
        "当前价接近或低于近期回购均价": "接近回购均价",
        "当前价显著高于近期回购均价": "显著高于均价",
        "当前价高于近期回购均价较多": "高于均价较多",
        "当前价处在52周区间中低位": "52周中低位",
        "当前价处在52周区间高位": "52周高位",
    }
    return replacements.get(reason, reason)


def _position_label(value):
    if value is None or pd.isna(value):
        return "N/A"
    if value <= 20:
        return "低位"
    if value <= 50:
        return "中低"
    if value < 80:
        return "中高"
    return "高位"


def _format_52_week_position(signal, snapshot=None, compact=False):
    price_position = (signal or {}).get("price_position_52")
    week_52_low = _snapshot_value(snapshot, "52周最低")
    week_52_high = _snapshot_value(snapshot, "52周最高")
    if price_position is None:
        return f"{format_price(week_52_low)}-{format_price(week_52_high)}"

    label = _position_label(price_position)
    text = f"{format_percent(price_position)} {label}"
    if compact:
        return text
    return f"{text} ({format_price(week_52_low)}-{format_price(week_52_high)})"


def _format_latest_buyback(signal):
    latest_buyback_date = (signal or {}).get("latest_buyback_date")
    gap_days = (signal or {}).get("buyback_gap_days")
    if latest_buyback_date is None or pd.isna(latest_buyback_date):
        return "N/A"

    date_text = pd.Timestamp(latest_buyback_date).strftime("%Y-%m-%d")
    if gap_days is None or pd.isna(gap_days):
        return date_text
    return f"{date_text} / {int(gap_days)}天前"


def _kpi_cell(label, value, style="bold"):
    return f"[cyan]{label}[/cyan] {f'[{style}]{value}[/{style}]' if style else value}"


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
    reasons = [_compact_reason(reason) for reason in signal.get("reasons", [])]
    reason_text = "  ".join(f"[{reason}]" for reason in reasons[:5]) if reasons else "[暂无明确触发项]"
    price_vs_text = format_signed_percent(signal.get("close_vs_buyback_price"))
    week_52_text = _format_52_week_position(signal, snapshot=report.get("basic_snapshot"), compact=True)

    overview_text = (
        f"[bold cyan]{title}[/bold cyan]  "
        f"[cyan]{latest_date_text}[/cyan]  "
        f"[bold {signal_color}]{signal['label']} {signal['score']}分[/bold {signal_color}]  "
        f"当前价 [bold]{format_price(signal.get('current_price'))}[/bold]  "
        f"相对均价 {price_vs_text}  "
        f"52周 {week_52_text}\n"
        f"{reason_text}"
    )
    console.print(
        Panel(
            overview_text,
            title="[bold cyan]回购分析助手[/bold cyan]",
            border_style=signal_color,
            expand=True,
        )
    )

    snapshot = report.get("basic_snapshot")
    window_metrics = report.get("window_metrics")
    kpi_table = _build_kpi_table(snapshot, signal, window_metrics)
    if kpi_table is not None:
        console.print(kpi_table)

    trend_table = _build_trend_table(
        report.get("monthly_summary"),
        report.get("yearly_summary"),
        month_rows=6,
        year_rows=2,
    )
    if trend_table is not None:
        console.print(trend_table)

    warnings = report.get("warnings") or []
    if warnings:
        warning_text = "；".join(warnings)
        console.print(f"[yellow]数据提示: {warning_text}[/yellow]")

    console.print(
        "[dim]提示: 回购仅作辅助参考，需结合基本面、市场环境和仓位管理。[/dim]"
    )


def _print_window_metrics(df):
    if df is None or df.empty:
        return

    console.print(_build_window_metrics_table(df))


def _build_window_metrics_table(df):
    if df is None or df.empty:
        return None

    table = Table(title="[bold cyan]近端回购强度[/bold cyan]", box=SIMPLE, header_style="bold magenta", expand=True)
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
    return table


def _print_basic_snapshot(snapshot):
    if snapshot is None:
        return

    console.print(_build_basic_snapshot_table(snapshot))


def _build_basic_snapshot_table(snapshot, signal=None):
    if snapshot is None:
        return None

    table = Table(title="[bold cyan]当前基础数据[/bold cyan]", box=SIMPLE, header_style="bold magenta", expand=True)
    table.add_column("字段", justify="center", style="cyan")
    table.add_column("数值", justify="right")
    for label, value in _basic_snapshot_rows(snapshot, signal):
        table.add_row(label, value)
    return table


def _basic_snapshot_rows(snapshot, signal=None):
    return [
        ("当前价", format_price(_snapshot_value(snapshot, "最新价"))),
        ("涨跌幅", format_percent(_snapshot_value(snapshot, "涨跌幅"))),
        ("成交额", format_compact_currency(_snapshot_value(snapshot, "成交额"))),
        ("总市值", format_compact_currency(_snapshot_value(snapshot, "总市值"))),
        ("港市值", format_compact_currency(_snapshot_value(snapshot, "港市值"))),
        ("市净率", format_price(_snapshot_value(snapshot, "市净率"))),
        ("换手率", format_percent(_snapshot_value(snapshot, "换手率"))),
        ("52周位置", _format_52_week_position(signal, snapshot)),
    ]


def _window_metric_lookup(df):
    if df is None or df.empty:
        return {}
    return {str(row["窗口"]): row for _, row in df.iterrows()}


def _window_kpi(label, row):
    if row is None:
        return _kpi_cell(label, "N/A")
    return _kpi_cell(
        label,
        (
            f"{format_compact_currency(row['回购总额'])} / "
            f"{int(row['回购天数'])}天 / "
            f"{format_price(row['加权均价'])}"
        ),
    )


def _build_kpi_table(snapshot, signal, window_df):
    if snapshot is None and (window_df is None or window_df.empty):
        return None

    windows = _window_metric_lookup(window_df)
    cells = [
        _kpi_cell("当前价", format_price((signal or {}).get("current_price"))),
        _kpi_cell("相对均价", format_signed_percent((signal or {}).get("close_vs_buyback_price"))),
        _kpi_cell("52周位置", _format_52_week_position(signal, snapshot, compact=True)),
        _kpi_cell("成交额", format_compact_currency(_snapshot_value(snapshot, "成交额"))),
        _kpi_cell("总市值", format_compact_currency(_snapshot_value(snapshot, "总市值"))),
        _kpi_cell("港市值", format_compact_currency(_snapshot_value(snapshot, "港市值"))),
        _kpi_cell("市净率", format_price(_snapshot_value(snapshot, "市净率"))),
        _kpi_cell("换手率", format_percent(_snapshot_value(snapshot, "换手率"))),
        _window_kpi("7天回购", windows.get("7天")),
        _window_kpi("30天回购", windows.get("30天")),
        _window_kpi("90天回购", windows.get("90天")),
        _kpi_cell("最近回购", _format_latest_buyback(signal)),
    ]

    columns = 4 if console.width >= 100 else 2
    table = Table(
        title="[bold cyan]当前数据 / 回购强度[/bold cyan]",
        box=SIMPLE,
        show_header=False,
        expand=True,
        padding=(0, 1),
    )
    for _ in range(columns):
        table.add_column(justify="left", overflow="fold")

    for index in range(0, len(cells), columns):
        row = cells[index:index + columns]
        table.add_row(*row, *[""] * (columns - len(row)))

    return table


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


def _build_trend_table(monthly_df, yearly_df, month_rows=6, year_rows=3):
    if (monthly_df is None or monthly_df.empty) and (yearly_df is None or yearly_df.empty):
        return None

    table = Table(title="[bold cyan]回购趋势[/bold cyan]", box=SIMPLE, header_style="bold magenta", expand=True)
    table.add_column("类型", justify="center", style="cyan", no_wrap=True)
    table.add_column("周期", justify="center", no_wrap=True)
    table.add_column("回购总额", justify="right", style="green")
    table.add_column("变化", justify="right")
    table.add_column("天数", justify="center", style="blue")
    table.add_column("均价", justify="right", style="red")

    if monthly_df is not None and not monthly_df.empty:
        for _, row in monthly_df.tail(month_rows).iterrows():
            table.add_row(
                "月",
                str(row["周期"]),
                format_compact_currency(row["回购总额"]),
                format_change(row["同比环比变化"]),
                str(int(row["回购天数"])),
                format_price(row["加权均价"]),
            )

    if yearly_df is not None and not yearly_df.empty:
        for _, row in yearly_df.tail(year_rows).iterrows():
            table.add_row(
                "年",
                str(row["周期"]),
                format_compact_currency(row["回购总额"]),
                format_change(row["同比环比变化"]),
                str(int(row["回购天数"])),
                format_price(row["加权均价"]),
            )

    return table
