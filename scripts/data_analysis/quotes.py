from datetime import date
from pathlib import Path

import pandas as pd
import requests
from rich.console import Console


console = Console()
DATA_DIR = Path(__file__).parent / "data"
DATA_SOURCE = "Eastmoney-QuotePage"
BASICS_COLUMNS = [
    "日期",
    "股票代码",
    "股票名称",
    "最新价",
    "今开",
    "最高",
    "最低",
    "昨收",
    "涨跌额",
    "涨跌幅",
    "成交量",
    "成交额",
    "总市值",
    "港市值",
    "市净率",
    "换手率",
    "52周最高",
    "52周最低",
    "数据源",
]
API_FIELDS = [
    "f43",
    "f44",
    "f45",
    "f46",
    "f47",
    "f48",
    "f51",
    "f52",
    "f57",
    "f58",
    "f59",
    "f60",
    "f116",
    "f117",
    "f152",
    "f167",
    "f168",
    "f169",
    "f170",
]


def normalize_stock_code(stock_code):
    """Normalize HK stock codes to five digits."""
    return str(stock_code).strip().zfill(5)


def basics_cache_path(stock_code):
    return DATA_DIR / f"basics_{normalize_stock_code(stock_code)}.csv"


def _missing(value):
    return value is None or value == "" or value == "-"


def _number(value):
    if _missing(value):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _scaled(value, digits):
    value = _number(value)
    digits = _number(digits)
    if value is None or digits is None:
        return None
    return value / (10 ** int(digits))


def _normalize_basic_frame(df):
    df = df.copy()
    for column in BASICS_COLUMNS:
        if column not in df.columns:
            df[column] = pd.NA
    df = df[BASICS_COLUMNS]
    if "日期" in df.columns:
        df["日期"] = pd.to_datetime(df["日期"]).dt.normalize()
    for column in [col for col in BASICS_COLUMNS if col not in ("日期", "股票代码", "股票名称", "数据源")]:
        df[column] = pd.to_numeric(df[column], errors="coerce")
    df.sort_values("日期", ascending=False, inplace=True)
    return df


def load_basic_data(stock_code):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    file_path = basics_cache_path(stock_code)
    if not file_path.exists():
        return pd.DataFrame(columns=BASICS_COLUMNS)

    return _normalize_basic_frame(pd.read_csv(file_path))


def save_basic_data(df, stock_code):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    file_path = basics_cache_path(stock_code)
    output_df = _normalize_basic_frame(df)
    output_df["日期"] = output_df["日期"].dt.strftime("%Y-%m-%d")
    output_df.to_csv(file_path, index=False)
    console.print(f"[green][OK][/green] Basic data saved to [bold]{file_path}[/bold]")


def fetch_basic_snapshot(stock_code, stock_name=None):
    """Fetch current HK stock basics from the Eastmoney quote page realtime API."""
    stock_code = normalize_stock_code(stock_code)
    quote_page = f"https://quote.eastmoney.com/hk/{stock_code}.html"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36"
        ),
        "Referer": quote_page,
    }

    with requests.Session() as session:
        page_response = session.get(quote_page, headers=headers, timeout=10)
        page_response.raise_for_status()

        api_response = session.get(
            "https://push2.eastmoney.com/api/qt/stock/get",
            headers=headers,
            params={
                "secid": f"116.{stock_code}",
                "fields": ",".join(API_FIELDS),
            },
            timeout=10,
        )
        api_response.raise_for_status()
        payload = api_response.json()

    if payload.get("rc") != 0 or not isinstance(payload.get("data"), dict):
        raise RuntimeError(f"Eastmoney realtime API returned invalid payload: {payload!r}")

    data = payload["data"]
    price_digits = data.get("f59")
    percent_digits = data.get("f152")
    api_name = data.get("f58")
    display_name = stock_name or api_name or ""

    return pd.DataFrame(
        [
            {
                "日期": date.today(),
                "股票代码": data.get("f57") or stock_code,
                "股票名称": display_name,
                "最新价": _scaled(data.get("f43"), price_digits),
                "今开": _scaled(data.get("f46"), price_digits),
                "最高": _scaled(data.get("f44"), price_digits),
                "最低": _scaled(data.get("f45"), price_digits),
                "昨收": _scaled(data.get("f60"), price_digits),
                "涨跌额": _scaled(data.get("f169"), price_digits),
                "涨跌幅": _scaled(data.get("f170"), percent_digits),
                "成交量": _number(data.get("f47")),
                "成交额": _number(data.get("f48")),
                "总市值": _number(data.get("f116")),
                "港市值": _number(data.get("f117")),
                "市净率": _scaled(data.get("f167"), percent_digits),
                "换手率": _scaled(data.get("f168"), percent_digits),
                "52周最高": _scaled(data.get("f51"), price_digits),
                "52周最低": _scaled(data.get("f52"), price_digits),
                "数据源": DATA_SOURCE,
            }
        ]
    )


def update_basic_data(stock_code, stock_name=None):
    """Load cached basics and upsert today's Eastmoney quote-page snapshot."""
    stock_code = normalize_stock_code(stock_code)
    cached_df = load_basic_data(stock_code)

    console.print(f"Checking basic quote data for [bold]{stock_code}[/bold]...")
    try:
        snapshot_df = _normalize_basic_frame(fetch_basic_snapshot(stock_code, stock_name))
    except Exception as exc:
        console.print(f"[yellow]Basic data update failed: {exc}. Using cached basic data.[/yellow]")
        return cached_df

    combined_df = snapshot_df.copy() if cached_df.empty else pd.concat([cached_df, snapshot_df], ignore_index=True)
    combined_df["日期"] = pd.to_datetime(combined_df["日期"]).dt.normalize()
    combined_df.drop_duplicates(subset=["日期"], keep="last", inplace=True)
    combined_df.sort_values("日期", ascending=False, inplace=True)
    save_basic_data(combined_df, stock_code)
    return combined_df
