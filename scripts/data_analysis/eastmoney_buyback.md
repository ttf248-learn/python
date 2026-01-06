# Eastmoney Buyback Data Scraper and Analyzer Usage

This script scrapes and analyzes stock buyback data from `hk.eastmoney.com`. It can fetch historical data, view it, and provide summaries grouped by year or month.

The data for each stock is saved locally in a CSV file under the `scripts/data_analysis/data/` directory. The script automatically updates this local data when run, so you always get the most current information combined with historical records.

## Installation

Before running the script, ensure you have the required Python packages installed:

```bash
pip install -r scripts/data_analysis/requirements.txt
```

## Commands and Usage

The script is command-line driven. Here are the available commands and how to use them.

### 1. `fetch`

**Purpose:** Fetches and updates the buyback data for a specific stock code. This command will scrape the website for any new data since the last fetch and merge it with the existing local data.

**Usage:**

```bash
python scripts/data_analysis/eastmoney_buyback.py fetch <stock_code>
```

**Example:**

To fetch and save the data for Tencent Holdings (00700):

```bash
python scripts/data_analysis/eastmoney_buyback.py fetch 00700
```

### 2. `view`

**Purpose:** Displays the most recent buyback data stored locally for a given stock. It will also trigger an update check before displaying.

**Usage:**

```bash
python scripts/data_analysis/eastmoney_buyback.py view <stock_code> [--limit <number_of_rows>]
```

-   `<stock_code>`: The stock code you want to view.
-   `--limit` (optional): The number of recent records to display. Defaults to 10.

**Examples:**

To view the latest 10 buyback records for Xiaomi (01810):

```bash
python scripts/data_analysis/eastmoney_buyback.py view 01810
```

To view the latest 25 records:

```bash
python scripts/data_analysis/eastmoney_buyback.py view 01810 --limit 25
```

### 3. `summary`

**Purpose:** Provides a summary of buyback activity, grouping the total amount, quantity, and average price by year or by month. This command also ensures the data is up-to-date before generating the summary.

**Usage:**

```bash
python scripts/data_analysis/eastmoney_buyback.py summary <stock_code> <period>
```

-   `<stock_code>`: The stock code for the summary.
-   `<period>`: The time frame to group by. Must be either `year` or `month`.

**Examples:**

To get an annual summary for Tencent (00700):

```bash
python scripts/data_analysis/eastmoney_buyback.py summary 00700 year
```

To get a monthly summary for Xiaomi (01810):

```bash
python scripts/data_analysis/eastmoney_buyback.py summary 01810 month
```
