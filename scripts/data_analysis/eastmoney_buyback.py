
import argparse
import os
import re
from pathlib import Path
from datetime import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup

# Define the data directory relative to the script's location
DATA_DIR = Path(__file__).parent / "data"

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
            print(f"Error fetching {url} (attempt {i+1}/{retries}): {e}")
    return None


def scrape_all_pages(stock_code, latest_date=None):
    """Scrapes all buyback data pages for a given stock code."""
    base_url = "https://hk.eastmoney.com"
    all_data = []
    
    with requests.Session() as session:
        # Scrape page 1
        page_url = f"{base_url}/buyback.html?code={stock_code}"
        print(f"Scraping page: {page_url}")
        soup = scrape_page(session, page_url)
        if not soup:
            print("Failed to fetch initial page. Aborting.")
            return pd.DataFrame()

        total_pages = get_total_pages(soup)
        print(f"Found {total_pages} pages for stock code {stock_code}.")

        # Process pages
        for page_num in range(1, total_pages + 1):
            if page_num > 1:
                page_url = f"{base_url}/buyback_{page_num}.html?code={stock_code}"
                print(f"Scraping page: {page_url}")
                soup = scrape_page(session, page_url)
                if not soup:
                    continue # Skip to next page if fetching fails

            table = soup.find('table', class_='table_striped')
            if not table:
                print(f"No data table found on page {page_num}.")
                continue
            
            rows = table.find('tbody').find_all('tr')
            page_has_new_data = False
            for row in rows:
                cols = [ele.text.strip() for ele in row.find_all('td')]
                if len(cols) == 9:
                    date_str = cols[8]
                    # Stop if we encounter a date we already have
                    if latest_date and datetime.strptime(date_str, '%Y-%m-%d').date() <= latest_date:
                        print(f"Reached existing data (date: {date_str}). Stopping incremental scrape.")
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
            
            # If the whole page had no new data, we can stop
            if not page_has_new_data and latest_date:
                return pd.DataFrame(all_data)

    return pd.DataFrame(all_data)


def load_stock_data(stock_code):
    """Loads existing data for a stock from a CSV file."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    file_path = DATA_DIR / f"{stock_code}.csv"
    if file_path.exists():
        print(f"Loading existing data from {file_path}")
        return pd.read_csv(file_path)
    return pd.DataFrame()

def save_stock_data(df, stock_code):
    """Saves DataFrame to a CSV file."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    file_path = DATA_DIR / f"{stock_code}.csv"
    df.to_csv(file_path, index=False)
    print(f"Data saved to {file_path}")

def update_stock_data(stock_code):
    """
    Fetches latest data, merges it with existing data, saves it, and returns the updated DataFrame.
    """
    existing_df = load_stock_data(stock_code)
    latest_date = None
    if not existing_df.empty and '日期' in existing_df.columns:
        # Convert to datetime objects and get the max date
        latest_date = pd.to_datetime(existing_df['日期']).max().date()

    print(f"Checking for new data for {stock_code}...")
    new_df = scrape_all_pages(stock_code, latest_date)

    if new_df.empty:
        print("No new data found. Using existing data.")
        return existing_df

    print("New data found, updating local store...")
    combined_df = pd.concat([new_df, existing_df], ignore_index=True)
    
    # Remove duplicates based on date, keeping the first occurrence (from new data)
    combined_df.drop_duplicates(subset=['日期'], keep='first', inplace=True)
    
    # Sort by date
    combined_df['日期'] = pd.to_datetime(combined_df['日期'])
    combined_df.sort_values(by='日期', ascending=False, inplace=True)
    
    save_stock_data(combined_df, stock_code)
    return combined_df

def show_summary(stock_code, period):
    """Shows a summary of buyback amounts by year or month after ensuring data is up-to-date."""
    df = update_stock_data(stock_code)
    
    if df.empty or '回购总额(港元)' not in df.columns or '回购数量(股)' not in df.columns:
        print(f"No data found or data is incomplete for stock {stock_code} even after attempting to fetch.")
        return

    df['日期'] = pd.to_datetime(df['日期'])
    
    # --- Grouping ---
    if period == 'year':
        group_by_col = df['日期'].dt.year
        group_by_col.name = 'Year'
    elif period == 'month':
        group_by_col = df['日期'].dt.to_period('M')
        group_by_col.name = 'YearMonth'
    else:
        print("Invalid summary period. Use 'year' or 'month'.")
        return

    summary_df = df.groupby(group_by_col).agg(
        TotalAmount=('回购总额(港元)', 'sum'),
        TotalQuantity=('回购数量(股)', 'sum')
    )
    summary_df['WeightedAvgPrice'] = summary_df['TotalAmount'] / summary_df['TotalQuantity']

    # --- Total Calculation ---
    total_amount = df['回购总额(港元)'].sum()
    total_quantity = df['回购数量(股)'].sum()
    total_avg_price = total_amount / total_quantity if total_quantity else 0

    # --- Formatting and Printing ---
    
    # Create a display DataFrame to avoid SettingWithCopyWarning
    display_df = pd.DataFrame()
    display_df['回购总额'] = summary_df['TotalAmount'].apply(lambda x: f"{x:,.2f} 港元")
    display_df['回购数量'] = summary_df['TotalQuantity'].apply(lambda x: f"{x:,.0f} 股")
    display_df['均价'] = summary_df['WeightedAvgPrice'].apply(lambda x: f"{x:.3f}")


    print(f"\n--- 回购总额汇总 ({'按' + ('年' if period == 'year' else '月')}) for {stock_code} ---")
    print(display_df)

    # Add total summary
    print("-" * 40)
    print("所有年份累加总计:")
    print(f"  回购总额: {total_amount:,.2f} 港元")
    print(f"  回购数量: {total_quantity:,.0f} 股")
    print(f"  加权均价: {total_avg_price:.3f}")
    print("---------------------------------------------------\n")

def view_data(stock_code, limit):
    """View the stored data after ensuring it is up-to-date."""
    df = update_stock_data(stock_code)

    if df.empty:
        print(f"No data found for stock {stock_code} even after attempting to fetch.")
        return

    print(f"\n--- Stored Data for {stock_code} (first {limit} rows) ---")
    with pd.option_context('display.max_rows', None, 'display.max_columns', None, 'display.width', 1000):
        print(df.head(limit))
    print("---------------------------------------------------\n")


def main():
    """Main function to handle command-line arguments."""
    parser = argparse.ArgumentParser(description="Eastmoney Buyback Data Scraper and Analyzer.")
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
    parser_summary.add_argument("period", type=str, choices=['year', 'month'], help="Summary period ('year' or 'month')")

    args = parser.parse_args()

    if args.command == "fetch":
        update_stock_data(args.code)
    elif args.command == "view":
        view_data(args.code, args.limit)
    elif args.command == "summary":
        show_summary(args.code, args.period)

if __name__ == "__main__":
    main()
