
import argparse
import re
from pathlib import Path
from datetime import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup
from rich.console import Console
from rich.progress import Progress

# Import custom display functions
from display import print_summary, print_data_view

# Initialize Rich Console
console = Console()

# Define the data directory relative to the script's location
DATA_DIR = Path(__file__).parent / "data"

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


def scrape_page(session, url, retries=3):
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
            console.print(f"[bold red]Error fetching {url} (attempt {i+1}/{retries}): {e}[/bold red]")
    return None


def scrape_all_pages(stock_code, latest_date=None):
    """Scrapes all buyback data pages for a given stock code with progress bar."""
    base_url = "https://hk.eastmoney.com"
    all_data = []

    with requests.Session() as session:
        page_url = f"{base_url}/buyback.html?code={stock_code}"
        soup = scrape_page(session, page_url)
        if not soup:
            console.print("[bold red]Failed to fetch initial page. Aborting.[/bold red]")
            return pd.DataFrame()

        total_pages = get_total_pages(soup)
        console.print(f"[green][OK][/green] Found [bold]{total_pages}[/bold] pages for stock code [bold]{stock_code}[/bold].")

        with Progress(console=console) as progress:
            task = progress.add_task(f"[cyan]Scraping {stock_code}...", total=total_pages)

            for page_num in range(1, total_pages + 1):
                progress.update(task, advance=1, description=f"[cyan]Scraping page {page_num}/{total_pages}")
                if page_num > 1:
                    page_url = f"{base_url}/buyback_{page_num}.html?code={stock_code}"
                    soup = scrape_page(session, page_url)
                    if not soup:
                        continue

                table = soup.find('table', class_='table_striped')
                if not table:
                    continue
                
                rows = table.find('tbody').find_all('tr')
                page_has_new_data = False
                for row in rows:
                    cols = [ele.text.strip() for ele in row.find_all('td')]
                    if len(cols) == 9:
                        date_str = cols[8]
                        if latest_date and datetime.strptime(date_str, '%Y-%m-%d').date() <= latest_date:
                            console.print(f"\n[yellow]![/yellow] Reached existing data (date: {date_str}). Stopping incremental scrape.")
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
                
                if not page_has_new_data and latest_date:
                    return pd.DataFrame(all_data)

    return pd.DataFrame(all_data)


def load_stock_data(stock_code):
    """Loads existing data for a stock from a CSV file."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    file_path = DATA_DIR / f"{stock_code}.csv"
    if file_path.exists():
        console.print(f"[green][OK][/green] Loading existing data from [bold]{file_path}[/bold]")
        return pd.read_csv(file_path)
    return pd.DataFrame()

def save_stock_data(df, stock_code):
    """Saves DataFrame to a CSV file."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    file_path = DATA_DIR / f"{stock_code}.csv"
    df.to_csv(file_path, index=False)
    console.print(f"[green][OK][/green] Data saved to [bold]{file_path}[/bold]")

def update_stock_data(stock_code):
    """
    Fetches latest data, merges it with existing data, saves it, and returns the updated DataFrame.
    """
    existing_df = load_stock_data(stock_code)
    latest_date = None
    if not existing_df.empty and '日期' in existing_df.columns:
        latest_date = pd.to_datetime(existing_df['日期']).max().date()

    console.print(f"Checking for new data for [bold]{stock_code}[/bold]...")
    new_df = scrape_all_pages(stock_code, latest_date)

    if new_df.empty:
        console.print("[yellow]No new data found. Using existing data.[/yellow]")
        return existing_df

    console.print("[green][OK][/green] New data found, updating local store...")
    combined_df = pd.concat([new_df, existing_df], ignore_index=True)
    
    combined_df.drop_duplicates(subset=['日期'], keep='first', inplace=True)
    
    combined_df['日期'] = pd.to_datetime(combined_df['日期'])
    combined_df.sort_values(by='日期', ascending=False, inplace=True)
    
    save_stock_data(combined_df, stock_code)
    return combined_df

def show_summary(stock_code, period, target_date=None):
    """Shows a summary of buyback amounts for a period or a specific date."""
    df = update_stock_data(stock_code)
    
    if df.empty or '回购总额(港元)' not in df.columns or '回购数量(股)' not in df.columns:
        console.print(f"[bold red]No data found or data is incomplete for stock {stock_code}.[/bold red]")
        return

    df['日期'] = pd.to_datetime(df['日期'])

    if period == 'date':
        if target_date is None:
            console.print("[bold red]A target date is required when period is 'date'.[/bold red]")
            return

        df = df[df['日期'].dt.date == target_date]
        if df.empty:
            console.print(
                f"[bold yellow]No buyback data found for stock {stock_code} on {target_date:%Y-%m-%d}.[/bold yellow]"
            )
            return
    
    # --- Grouping ---
    if period == 'year':
        group_by_col = df['日期'].dt.year
        group_by_col.name = 'Year'
    elif period == 'month':
        group_by_col = df['日期'].dt.to_period('M')
        group_by_col.name = 'YearMonth'
    elif period == 'date':
        group_by_col = df['日期'].dt.date
        group_by_col.name = 'Date'
    else:
        console.print("[bold red]Invalid summary period. Use 'year', 'month', or 'date'.[/bold red]")
        return

    summary_df = df.groupby(group_by_col).agg(
        TotalAmount=('回购总额(港元)', 'sum'),
        TotalQuantity=('回购数量(股)', 'sum'),
        BuybackDays=('日期', 'count'),  # Number of buyback days in the period
        AvgDailyAmount=('回购总额(港元)', 'mean') # Average daily buyback amount
    )
    # Use a small epsilon to avoid division by zero
    summary_df['WeightedAvgPrice'] = summary_df['TotalAmount'] / (summary_df['TotalQuantity'] + 1e-9)
    
    # Calculate Period-over-Period Change
    summary_df['PoP_Change'] = summary_df['TotalAmount'].pct_change(periods=-1) * 100 # Change from previous period



    # --- Total Calculation ---
    total_amount = df['回购总额(港元)'].sum()
    total_quantity = df['回购数量(股)'].sum()
    total_avg_price = total_amount / total_quantity if total_quantity else 0

    # --- Use Rich for printing ---
    print_summary(df, stock_code, period, summary_df, total_amount, total_quantity, total_avg_price)


def view_data(stock_code, limit):
    """View the stored data after ensuring it is up-to-date."""
    df = update_stock_data(stock_code)
    print_data_view(df, stock_code, limit)


def main():
    """Main function to handle command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Eastmoney Buyback Data Scraper and Analyzer.",
        epilog="Examples: python eastmoney_buyback.py summary 00700 year | python eastmoney_buyback.py summary 00700 date 2026-01-15"
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

if __name__ == "__main__":
    main()
