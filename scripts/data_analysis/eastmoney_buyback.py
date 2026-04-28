
import argparse
import re
import sys
from pathlib import Path
from datetime import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup
from rich.console import Console
from rich.progress import BarColumn, Progress, TaskProgressColumn, TextColumn, TimeElapsedColumn, TimeRemainingColumn

# Import custom display functions
from analyzer import build_analysis_report, export_analysis_report
from display import print_analysis_report, print_summary, print_data_view
from quotes import load_basic_data, normalize_stock_code, update_basic_data

# Initialize Rich Console
console = Console()

# Define the data directory relative to the script's location
APP_DIR = Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).parent
DATA_DIR = APP_DIR / "data"

def parse_cli_date(date_str):
    """Parses a CLI date argument in YYYY-MM-DD format."""
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"Invalid date '{date_str}'. Expected format: YYYY-MM-DD."
        ) from exc

def parse_value(value_str):
    """Converts string values like '105.40万' to a float."""
    if isinstance(value_str, (int, float)):
        return value_str
    if not isinstance(value_str, str):
        return None

    value_str = value_str.strip()
    if '万' in value_str:
        return float(value_str.replace('万', '')) * 10000
    if '亿' in value_str:
        return float(value_str.replace('亿', '')) * 100000000
    try:
        return float(value_str)
    except (ValueError, TypeError):
        return None

def get_total_pages(soup):
    """Extracts the total number of pages from the pagination section."""
    pager = soup.find('div', class_='pager')
    if not pager:
        return 1
    
    # Find the link before the "下一页" (next page) link
    next_page_link = pager.find('a', string='下一页')
    if next_page_link and next_page_link.previous_sibling and next_page_link.previous_sibling.name == 'a':
        last_page_href = next_page_link.previous_sibling['href']
        match = re.search(r'buyback_(\d+)\.html', last_page_href)
        if match:
            return int(match.group(1))

    # Fallback for single page or if the above logic fails
    links = pager.find_all('a')
    if not links:
        return 1

    max_page = 1
    for link in links:
        href = link.get('href', '')
        match = re.search(r'buyback_(\d+)\.html', href)
        if match:
            page_num = int(match.group(1))
            if page_num > max_page:
                max_page = page_num
    return max_page


def scrape_page(session, url, retries=3, verbose=True):
    """Fetches and parses a single page."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    for i in range(retries):
        try:
            response = session.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            # The page is encoded in utf-8
            response.encoding = 'utf-8'
            return BeautifulSoup(response.text, 'lxml')
        except requests.exceptions.RequestException as e:
            if verbose:
                console.print(f"[bold red]Error fetching {url} (attempt {i+1}/{retries}): {e}[/bold red]")
    return None


def scrape_all_pages(stock_code, latest_date=None, verbose=True):
    """Scrapes all buyback data pages for a given stock code with progress bar."""
    base_url = "https://hk.eastmoney.com"
    all_data = []

    with requests.Session() as session:
        page_url = f"{base_url}/buyback.html?code={stock_code}"
        soup = scrape_page(session, page_url, verbose=verbose)
        if not soup:
            console.print("[yellow]Buyback data update failed. Using cached buyback data if available.[/yellow]")
            return pd.DataFrame()

        total_pages = get_total_pages(soup)
        if verbose:
            console.print(f"[green][OK][/green] Found [bold]{total_pages}[/bold] pages for stock code [bold]{stock_code}[/bold].")

        if not verbose:
            progress = None
            task = None
            task_total = None
        elif latest_date:
            progress = Progress(
                TextColumn("[progress.description]{task.description}"),
                TimeElapsedColumn(),
                console=console,
            )
            task_total = None
        else:
            progress = Progress(
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                TimeRemainingColumn(),
                console=console,
            )
            task_total = total_pages

        def scan_pages(progress=None, task=None, task_total=None):
            for page_num in range(1, total_pages + 1):
                if progress is not None and latest_date:
                    progress.update(task, description=f"[cyan]Checking page {page_num}")
                elif progress is not None:
                    progress.update(task, description=f"[cyan]Scraping page {page_num}/{total_pages}")

                page_soup = soup
                if page_num > 1:
                    page_url = f"{base_url}/buyback_{page_num}.html?code={stock_code}"
                    page_soup = scrape_page(session, page_url, verbose=verbose)
                    if not page_soup:
                        if task_total is not None:
                            progress.advance(task)
                        continue

                table = page_soup.find('table', class_='table_striped')
                if not table:
                    if task_total is not None:
                        progress.advance(task)
                    continue
                
                rows = table.find('tbody').find_all('tr')
                page_has_new_data = False
                for row in rows:
                    cols = [ele.text.strip() for ele in row.find_all('td')]
                    if len(cols) == 9:
                        date_str = cols[8]
                        if latest_date and datetime.strptime(date_str, '%Y-%m-%d').date() <= latest_date:
                            if verbose:
                                console.print(
                                    f"\n[yellow]![/yellow] Reached local data boundary at {date_str}. Stopping incremental update."
                                )
                            return pd.DataFrame(all_data)

                        page_has_new_data = True
                        data = {
                            '股票代码': cols[1],
                            '股票名称': cols[2],
                            '回购数量(股)': parse_value(cols[3]),
                            '最高回购价': parse_value(cols[4]),
                            '最低回购价': parse_value(cols[5]),
                            '回购平均价': parse_value(cols[6]),
                            '回购总额(港元)': parse_value(cols[7]),
                            '日期': date_str,
                        }
                        all_data.append(data)

                if task_total is not None:
                    progress.advance(task)
                
                if not page_has_new_data and latest_date:
                    return pd.DataFrame(all_data)

            return pd.DataFrame(all_data)

        if progress is None:
            return scan_pages()

        with progress:
            task = progress.add_task(f"[cyan]Scanning {stock_code}...", total=task_total)
            return scan_pages(progress, task, task_total)

    return pd.DataFrame(all_data)


def load_stock_data(stock_code, verbose=True):
    """Loads existing data for a stock from a CSV file."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    file_path = DATA_DIR / f"{stock_code}.csv"
    if file_path.exists():
        if verbose:
            console.print(f"[green][OK][/green] Loading existing data from [bold]{file_path}[/bold]")
        df = pd.read_csv(file_path)
        if "日期" in df.columns:
            df["日期"] = pd.to_datetime(df["日期"])
        return df
    return pd.DataFrame()

def save_stock_data(df, stock_code, verbose=True):
    """Saves DataFrame to a CSV file."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    file_path = DATA_DIR / f"{stock_code}.csv"
    df.to_csv(file_path, index=False)
    if verbose:
        console.print(f"[green][OK][/green] Data saved to [bold]{file_path}[/bold]")

def update_stock_data(stock_code, verbose=True):
    """
    Fetches latest data, merges it with existing data, saves it, and returns the updated DataFrame.
    """
    existing_df = load_stock_data(stock_code, verbose=verbose)
    latest_date = None
    if not existing_df.empty and '日期' in existing_df.columns:
        latest_date = pd.to_datetime(existing_df['日期']).max().date()

    if verbose:
        console.print(f"Checking for new data for [bold]{stock_code}[/bold]...")
    new_df = scrape_all_pages(stock_code, latest_date, verbose=verbose)

    if new_df.empty:
        if verbose:
            console.print("[yellow]No new data found. Using existing data.[/yellow]")
        return existing_df

    if verbose:
        console.print("[green][OK][/green] New data found, updating local store...")
    combined_df = pd.concat([new_df, existing_df], ignore_index=True)
    
    combined_df.drop_duplicates(subset=['日期'], keep='first', inplace=True)
    
    combined_df['日期'] = pd.to_datetime(combined_df['日期'])
    combined_df.sort_values(by='日期', ascending=False, inplace=True)
    
    save_stock_data(combined_df, stock_code, verbose=verbose)
    return combined_df


def build_daily_summary_data(df):
    """Aggregates raw buyback records into one row per date for stable summary stats."""
    daily_df = df.copy()
    daily_df['日期'] = pd.to_datetime(daily_df['日期']).dt.normalize()

    daily_df = daily_df.groupby('日期', as_index=False).agg(
        回购总额港元=('回购总额(港元)', 'sum'),
        回购数量股=('回购数量(股)', 'sum'),
    )
    daily_df.rename(
        columns={
            '回购总额港元': '回购总额(港元)',
            '回购数量股': '回购数量(股)',
        },
        inplace=True,
    )
    return daily_df

def show_summary(stock_code, period, target_date=None):
    """Shows a summary of buyback amounts for a period or a specific date."""
    df = update_stock_data(stock_code)
    
    if df.empty or '回购总额(港元)' not in df.columns or '回购数量(股)' not in df.columns:
        console.print(f"[bold red]No data found or data is incomplete for stock {stock_code}.[/bold red]")
        return

    summary_source_df = build_daily_summary_data(df)

    period_label = None

    if period == 'date':
        if target_date is None:
            console.print("[bold red]A target date is required when period is 'date'.[/bold red]")
            return

        summary_source_df = summary_source_df[summary_source_df['日期'].dt.date >= target_date]
        if summary_source_df.empty:
            console.print(
                f"[bold yellow]No buyback data found for stock {stock_code} from {target_date:%Y-%m-%d} onward.[/bold yellow]"
            )
            return

        end_date = summary_source_df['日期'].max().date()
        period_label = f"{target_date:%Y-%m-%d} 至 {end_date:%Y-%m-%d}"
    
    # --- Grouping ---
    if period == 'year':
        group_by_col = summary_source_df['日期'].dt.year
        group_by_col.name = 'Year'
    elif period == 'month':
        group_by_col = summary_source_df['日期'].dt.to_period('M')
        group_by_col.name = 'YearMonth'
    elif period == 'date':
        group_by_col = pd.Series(period_label, index=summary_source_df.index, name='DateRange')
    else:
        console.print("[bold red]Invalid summary period. Use 'year', 'month', or 'date'.[/bold red]")
        return

    summary_df = summary_source_df.groupby(group_by_col).agg(
        TotalAmount=('回购总额(港元)', 'sum'),
        TotalQuantity=('回购数量(股)', 'sum'),
        BuybackDays=('日期', 'size'),
        AvgDailyAmount=('回购总额(港元)', 'mean')
    )
    # Use a small epsilon to avoid division by zero
    summary_df['WeightedAvgPrice'] = summary_df['TotalAmount'] / (summary_df['TotalQuantity'] + 1e-9)
    
    # Calculate Period-over-Period Change
    summary_df['PoP_Change'] = summary_df['TotalAmount'].pct_change(periods=-1) * 100 # Change from previous period



    # --- Total Calculation ---
    total_amount = summary_source_df['回购总额(港元)'].sum()
    total_quantity = summary_source_df['回购数量(股)'].sum()
    total_avg_price = total_amount / total_quantity if total_quantity else 0

    # --- Use Rich for printing ---
    print_summary(
        summary_source_df,
        stock_code,
        period,
        summary_df,
        total_amount,
        total_quantity,
        total_avg_price,
        target_date,
        period_label,
    )


def view_data(stock_code, limit):
    """View the stored data after ensuring it is up-to-date."""
    df = update_stock_data(stock_code)
    print_data_view(df, stock_code, limit)


def analyze_stock(stock_code, window="1y", should_update=True, should_export=False, verbose=False):
    """Build and display a trading-oriented buyback analysis report."""
    stock_code = normalize_stock_code(stock_code)
    if should_update:
        buyback_df = update_stock_data(stock_code, verbose=verbose)
    else:
        buyback_df = load_stock_data(stock_code, verbose=verbose)

    if buyback_df.empty:
        console.print(f"[bold red]No buyback data found for stock {stock_code}.[/bold red]")
        return

    stock_name = None
    if "股票名称" in buyback_df.columns and not buyback_df.empty:
        stock_name = str(buyback_df.iloc[0]["股票名称"])

    if should_update:
        basic_df = update_basic_data(stock_code, stock_name, verbose=verbose)
    else:
        basic_df = load_basic_data(stock_code)

    report = build_analysis_report(stock_code, buyback_df, basic_df, window)
    print_analysis_report(report)

    if should_export:
        files = export_analysis_report(report, DATA_DIR)
        for file_path in files:
            console.print(f"[green][OK][/green] Analysis exported to [bold]{file_path}[/bold]")


def main():
    """Main function to handle command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Eastmoney Buyback Data Scraper and Analysis Assistant.",
        epilog="Examples: python eastmoney_buyback.py analyze 01810 | python eastmoney_buyback.py summary 00700 year"
    )
    subparsers = parser.add_subparsers(dest="command", required=True, help="Available commands")

    # Fetch command
    parser_fetch = subparsers.add_parser("fetch", help="Fetch and update buyback data for a stock.")
    parser_fetch.add_argument("code", type=str, help="Stock code (e.g., 00700)")

    # View command
    parser_view = subparsers.add_parser("view", help="View stored data for a stock.")
    parser_view.add_argument("code", type=str, help="Stock code (e.g., 00700)")
    parser_view.add_argument("--limit", type=int, default=10, help="Number of rows to display (default: 10)")

    # Summary command
    parser_summary = subparsers.add_parser("summary", help="Show summary of buyback data.")
    parser_summary.add_argument("code", type=str, help="Stock code (e.g., 00700)")
    parser_summary.add_argument("period", type=str, choices=['year', 'month', 'date'], help="Summary period ('year', 'month', or 'date')")
    parser_summary.add_argument("target_date", nargs='?', type=parse_cli_date, help="Required when period is 'date'. Format: YYYY-MM-DD")

    # Analyze command
    parser_analyze = subparsers.add_parser("analyze", help="Analyze buyback data for trading assistance.")
    parser_analyze.add_argument("code", type=str, help="Stock code (e.g., 01810)")
    parser_analyze.add_argument(
        "--window",
        choices=["1y", "3y", "all"],
        default="1y",
        help="Analysis window (default: 1y)",
    )
    parser_analyze.add_argument(
        "--no-update",
        action="store_true",
        help="Use local cached buyback and basic quote data without fetching updates.",
    )
    parser_analyze.add_argument(
        "--export",
        action="store_true",
        help="Export analysis tables to CSV files in the data directory.",
    )
    parser_analyze.add_argument(
        "--verbose",
        action="store_true",
        help="Show update progress and cache logs before the analysis report.",
    )

    args = parser.parse_args()

    if args.command == "fetch":
        update_stock_data(args.code)
    elif args.command == "view":
        view_data(args.code, args.limit)
    elif args.command == "summary":
        if args.period == "date" and args.target_date is None:
            parser.error("summary period 'date' requires target_date in YYYY-MM-DD format")
        if args.period != "date" and args.target_date is not None:
            parser.error("target_date is only supported when summary period is 'date'")
        show_summary(args.code, args.period, args.target_date)
    elif args.command == "analyze":
        analyze_stock(args.code, args.window, not args.no_update, args.export, args.verbose)

if __name__ == "__main__":
    main()
