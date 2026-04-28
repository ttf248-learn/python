from datetime import timedelta
from pathlib import Path

import pandas as pd


WINDOW_DAYS = (7, 30, 90)


def prepare_buyback_daily(df):
    """Aggregate buyback records to one row per date."""
    if df.empty:
        return pd.DataFrame()

    daily_df = df.copy()
    daily_df["日期"] = pd.to_datetime(daily_df["日期"]).dt.normalize()
    daily_df["回购总额(港元)"] = pd.to_numeric(daily_df["回购总额(港元)"], errors="coerce").fillna(0)
    daily_df["回购数量(股)"] = pd.to_numeric(daily_df["回购数量(股)"], errors="coerce").fillna(0)

    grouped = daily_df.groupby("日期", as_index=False).agg(
        股票代码=("股票代码", "first"),
        股票名称=("股票名称", "first"),
        回购总额港元=("回购总额(港元)", "sum"),
        回购数量股=("回购数量(股)", "sum"),
        最高回购价=("最高回购价", "max"),
        最低回购价=("最低回购价", "min"),
    )
    grouped.rename(
        columns={
            "回购总额港元": "回购总额(港元)",
            "回购数量股": "回购数量(股)",
        },
        inplace=True,
    )
    grouped["回购加权均价"] = grouped["回购总额(港元)"] / grouped["回购数量(股)"].replace(0, pd.NA)
    grouped.sort_values("日期", ascending=False, inplace=True)
    return grouped


def filter_by_window(df, latest_date, window):
    if df.empty or window == "all":
        return df.copy()

    years = 1 if window == "1y" else 3
    start_date = latest_date - pd.DateOffset(years=years)
    return df[pd.to_datetime(df["日期"]) >= start_date].copy()


def build_period_summary(daily_df, period):
    if daily_df.empty:
        return pd.DataFrame()

    source_df = daily_df.copy()
    source_df["日期"] = pd.to_datetime(source_df["日期"]).dt.normalize()
    if period == "month":
        source_df["周期"] = source_df["日期"].dt.to_period("M").astype(str)
    elif period == "year":
        source_df["周期"] = source_df["日期"].dt.year.astype(str)
    else:
        raise ValueError("period must be 'month' or 'year'")

    summary_df = source_df.groupby("周期", as_index=False).agg(
        回购总额=("回购总额(港元)", "sum"),
        回购数量=("回购数量(股)", "sum"),
        回购天数=("日期", "size"),
        日均回购额=("回购总额(港元)", "mean"),
    )
    summary_df["加权均价"] = summary_df["回购总额"] / summary_df["回购数量"].replace(0, pd.NA)
    summary_df["同比环比变化"] = summary_df["回购总额"].pct_change() * 100
    return summary_df


def _sum_between(df, date_col, start_date, end_date):
    if df.empty:
        return df.copy()
    mask = (pd.to_datetime(df[date_col]) >= pd.Timestamp(start_date)) & (
        pd.to_datetime(df[date_col]) <= pd.Timestamp(end_date)
    )
    return df.loc[mask].copy()


def _pct_change(current, previous):
    if previous is None or pd.isna(previous) or previous == 0:
        return None
    return (current - previous) / previous * 100


def _safe_divide(numerator, denominator):
    if denominator is None or pd.isna(denominator) or denominator == 0:
        return None
    return numerator / denominator


def build_window_metrics(daily_df, latest_date):
    rows = []
    for days in WINDOW_DAYS:
        start_date = latest_date - timedelta(days=days - 1)
        buyback_part = _sum_between(daily_df, "日期", start_date, latest_date)

        amount = buyback_part["回购总额(港元)"].sum() if not buyback_part.empty else 0
        quantity = buyback_part["回购数量(股)"].sum() if not buyback_part.empty else 0
        weighted_price = _safe_divide(amount, quantity)

        rows.append(
            {
                "窗口": f"{days}天",
                "回购总额": amount,
                "回购天数": int(buyback_part["日期"].nunique()) if not buyback_part.empty else 0,
                "加权均价": weighted_price,
            }
        )

    return pd.DataFrame(rows)


def latest_basic_snapshot(basic_df):
    if basic_df is None or basic_df.empty or "日期" not in basic_df.columns:
        return None
    sorted_df = basic_df.copy()
    sorted_df["日期"] = pd.to_datetime(sorted_df["日期"]).dt.normalize()
    sorted_df.sort_values("日期", ascending=False, inplace=True)
    return sorted_df.iloc[0]


def _value(snapshot, column):
    if snapshot is None or column not in snapshot:
        return None
    value = snapshot[column]
    if pd.isna(value):
        return None
    return value


def calculate_signal(daily_df, basic_snapshot, latest_date):
    current_30 = _sum_between(daily_df, "日期", latest_date - timedelta(days=29), latest_date)
    previous_30 = _sum_between(daily_df, "日期", latest_date - timedelta(days=59), latest_date - timedelta(days=30))
    current_90 = _sum_between(daily_df, "日期", latest_date - timedelta(days=89), latest_date)

    amount_30 = current_30["回购总额(港元)"].sum() if not current_30.empty else 0
    prev_amount_30 = previous_30["回购总额(港元)"].sum() if not previous_30.empty else 0
    amount_90 = current_90["回购总额(港元)"].sum() if not current_90.empty else 0
    acceleration_30 = _pct_change(amount_30, prev_amount_30)

    latest_buyback_date = daily_df["日期"].max() if not daily_df.empty else None
    buyback_gap_days = None
    if latest_buyback_date is not None and not pd.isna(latest_buyback_date):
        buyback_gap_days = (pd.Timestamp(latest_date) - pd.Timestamp(latest_buyback_date)).days

    recent_amount = amount_30 if amount_30 > 0 else amount_90
    recent_quantity = (
        current_30["回购数量(股)"].sum()
        if amount_30 > 0 and not current_30.empty
        else current_90["回购数量(股)"].sum()
        if not current_90.empty
        else 0
    )
    recent_buyback_price = _safe_divide(recent_amount, recent_quantity)

    current_price = _value(basic_snapshot, "最新价")
    close_vs_buyback_price = None
    if current_price is not None and recent_buyback_price:
        close_vs_buyback_price = (current_price - recent_buyback_price) / recent_buyback_price * 100

    week_52_high = _value(basic_snapshot, "52周最高")
    week_52_low = _value(basic_snapshot, "52周最低")
    price_position_52 = None
    if current_price is not None and week_52_high and week_52_low and week_52_high != week_52_low:
        price_position_52 = (current_price - week_52_low) / (week_52_high - week_52_low) * 100

    score = 0
    reasons = []

    if amount_30 > 0:
        score += 1
        reasons.append("近30天仍有回购")
    else:
        score -= 2
        reasons.append("近30天未观察到回购")

    if acceleration_30 is not None:
        if acceleration_30 >= 50:
            score += 2
            reasons.append("近30天回购较前30天明显加速")
        elif acceleration_30 >= 10:
            score += 1
            reasons.append("近30天回购较前30天温和加速")
        elif acceleration_30 <= -50:
            score -= 2
            reasons.append("近30天回购较前30天明显减速")
        elif acceleration_30 <= -20:
            score -= 1
            reasons.append("近30天回购较前30天有所减速")

    if buyback_gap_days is not None:
        if buyback_gap_days <= 7:
            score += 1
            reasons.append("最近一周内有回购记录")
        elif buyback_gap_days > 30:
            score -= 2
            reasons.append("最近一次回购距离当前超过30天")
        elif buyback_gap_days > 14:
            score -= 1
            reasons.append("最近一次回购距离当前超过两周")

    if close_vs_buyback_price is not None:
        if close_vs_buyback_price <= 5:
            score += 1
            reasons.append("当前价接近或低于近期回购均价")
        elif close_vs_buyback_price > 30:
            score -= 2
            reasons.append("当前价显著高于近期回购均价")
        elif close_vs_buyback_price > 15:
            score -= 1
            reasons.append("当前价高于近期回购均价较多")

    if price_position_52 is not None:
        if price_position_52 <= 50:
            score += 1
            reasons.append("当前价处在52周区间中低位")
        elif price_position_52 >= 80:
            score -= 1
            reasons.append("当前价处在52周区间高位")

    if score >= 4:
        label = "偏积极"
    elif score <= -2:
        label = "偏谨慎"
    else:
        label = "观察"

    return {
        "label": label,
        "score": score,
        "reasons": reasons[:5],
        "amount_30": amount_30,
        "prev_amount_30": prev_amount_30,
        "amount_90": amount_90,
        "acceleration_30": acceleration_30,
        "buyback_gap_days": buyback_gap_days,
        "current_price": current_price,
        "price_position_52": price_position_52,
        "recent_buyback_price": recent_buyback_price,
        "close_vs_buyback_price": close_vs_buyback_price,
    }


def build_analysis_report(stock_code, buyback_df, basic_df, window="1y"):
    daily_df = prepare_buyback_daily(buyback_df)
    if daily_df.empty:
        return {
            "stock_code": stock_code,
            "stock_name": "",
            "warnings": ["没有可分析的回购数据"],
            "daily": daily_df,
            "basics": basic_df,
        }

    basic_df = basic_df.copy()
    if not basic_df.empty and "日期" in basic_df:
        basic_df["日期"] = pd.to_datetime(basic_df["日期"]).dt.normalize()
        basic_df.sort_values("日期", ascending=False, inplace=True)

    latest_candidates = [daily_df["日期"].max()]
    if not basic_df.empty:
        latest_candidates.append(basic_df["日期"].max())
    latest_date = max(pd.Timestamp(value) for value in latest_candidates if pd.notna(value))

    scoped_daily = filter_by_window(daily_df, latest_date, window)
    basic_snapshot = latest_basic_snapshot(basic_df)
    monthly_summary = build_period_summary(scoped_daily, "month")
    yearly_summary = build_period_summary(scoped_daily, "year")
    window_metrics = build_window_metrics(scoped_daily, latest_date)
    signal = calculate_signal(scoped_daily, basic_snapshot, latest_date)

    warnings = []
    if basic_df.empty:
        warnings.append("基础数据缺失，仅输出回购分析")
    if signal["current_price"] is None:
        warnings.append("没有可用当前价，无法比较当前价与回购均价")
    if signal["price_position_52"] is None:
        warnings.append("缺少52周区间数据，当前价区间位置已降级")

    stock_name = ""
    if "股票名称" in scoped_daily.columns and not scoped_daily.empty:
        stock_name = str(scoped_daily.iloc[0]["股票名称"])
    if not stock_name and basic_snapshot is not None:
        stock_name = str(_value(basic_snapshot, "股票名称") or "")

    return {
        "stock_code": stock_code,
        "stock_name": stock_name,
        "latest_date": latest_date,
        "window": window,
        "signal": signal,
        "basic_snapshot": basic_snapshot,
        "window_metrics": window_metrics,
        "monthly_summary": monthly_summary,
        "yearly_summary": yearly_summary,
        "daily": scoped_daily,
        "basics": basic_df,
        "warnings": warnings,
    }


def export_analysis_report(report, output_dir):
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    code = report["stock_code"]
    latest = report.get("latest_date")
    suffix = latest.strftime("%Y%m%d") if latest is not None else "latest"

    files = []
    for name, key in (
        ("windows", "window_metrics"),
        ("monthly", "monthly_summary"),
        ("yearly", "yearly_summary"),
        ("basics", "basics"),
    ):
        df = report.get(key)
        if isinstance(df, pd.DataFrame) and not df.empty:
            file_path = output_path / f"analysis_{code}_{suffix}_{name}.csv"
            df.to_csv(file_path, index=False)
            files.append(file_path)
    return files
