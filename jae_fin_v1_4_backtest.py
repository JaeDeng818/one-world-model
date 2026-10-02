# -*- coding: utf-8 -*-
"""
JAE-FIN v1.4 回测引擎
======================
目标：
1. 历史滚动计算 JAE-FIN 六因子评分
2. 生成历史信号
3. 计算信号后的收益、最大回撤、胜率
4. 基准对比
5. 参数敏感性分析
6. 防止未来函数：每个交易日只使用当日收盘以前可获得的信息，
   信号默认在下一交易日开盘/收盘近似成交。

依赖：
    pip install akshare pandas numpy openpyxl

示例：
    python jae_fin_v1_4_backtest.py --start 20230101 --end 20261001

输出：
    jae_fin_v1_4_backtest.xlsx

注意：
- 这是研究/验证工具，不是收益保证。
- 财务数据若没有可靠的历史时点接口，本版本默认不把未来财报数据倒灌到历史。
- 为避免“后视偏差”，v1.4核心回测使用纯历史行情因子：
  技术、趋势、波动、回撤、相对强弱。
- 基本面/资金面可通过 --fundamental-file 接入“带发布日期”的历史数据。
"""

import argparse
import itertools
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")


WATCHLIST = {
    "688256": ("寒武纪", "AI芯片"),
    "300308": ("中际旭创", "AI光通信"),
    "002463": ("沪电股份", "AI服务器PCB"),
    "002371": ("北方华创", "半导体设备"),
    "688012": ("中微公司", "半导体设备"),
    "600089": ("特变电工", "电力/能源"),
    "600406": ("国电南瑞", "电网/电力数字化"),
    "601899": ("紫金矿业", "黄金/铜资源"),
    "600900": ("长江电力", "水电/高股息"),
    "688981": ("中芯国际", "晶圆制造"),
}


# ----------------------------
# 通用工具
# ----------------------------

def norm(x, bad, good):
    x = np.asarray(x, dtype=float)
    out = np.full(x.shape, 50.0)
    valid = np.isfinite(x)
    out[valid] = np.where(
        x[valid] <= bad, 0,
        np.where(x[valid] >= good, 100,
                 100 * (x[valid] - bad) / (good - bad))
    )
    return out


def inv_norm(x, good, bad):
    x = np.asarray(x, dtype=float)
    out = np.full(x.shape, 50.0)
    valid = np.isfinite(x)
    out[valid] = np.where(
        x[valid] <= good, 100,
        np.where(x[valid] >= bad, 0,
                 100 * (bad - x[valid]) / (bad - good))
    )
    return out


def max_drawdown(equity):
    equity = pd.Series(equity).astype(float)
    peak = equity.cummax()
    dd = equity / peak - 1
    return float(dd.min())


def annualized_return(equity, periods_per_year=252):
    equity = pd.Series(equity).dropna()
    if len(equity) < 2 or equity.iloc[0] <= 0:
        return np.nan
    years = len(equity) / periods_per_year
    return float((equity.iloc[-1] / equity.iloc[0]) ** (1 / years) - 1)


def sharpe(returns, periods_per_year=252):
    r = pd.Series(returns).dropna()
    if len(r) < 2 or r.std() == 0:
        return np.nan
    return float(np.sqrt(periods_per_year) * r.mean() / r.std())


# ----------------------------
# 数据
# ----------------------------

def load_akshare():
    try:
        import akshare as ak
        return ak
    except ImportError:
        raise SystemExit(
            "缺少AkShare，请执行：pip install akshare pandas numpy openpyxl"
        )


def get_history(ak, code, start, end):
    df = ak.stock_zh_a_hist(
        symbol=code,
        period="daily",
        start_date=start,
        end_date=end,
        adjust="qfq"
    )

    if df is None or df.empty:
        return pd.DataFrame()

    rename = {
        "日期": "date",
        "开盘": "open",
        "收盘": "close",
        "最高": "high",
        "最低": "low",
        "成交量": "volume",
        "成交额": "amount",
    }
    df = df.rename(columns=rename)

    need = ["date", "open", "close", "high", "low", "volume"]
    for c in need:
        if c not in df.columns:
            return pd.DataFrame()

    df["date"] = pd.to_datetime(df["date"])
    for c in need[1:]:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    return df.sort_values("date").reset_index(drop=True)


# ----------------------------
# 历史因子
# ----------------------------

def build_features(df, ma_fast=20, ma_mid=60, ma_slow=200,
                   rsi_window=14, vol_window=60, dd_window=120):

    x = df.copy()
    c = x["close"]
    v = x["volume"]

    x["ma_fast"] = c.rolling(ma_fast).mean()
    x["ma_mid"] = c.rolling(ma_mid).mean()
    x["ma_slow"] = c.rolling(ma_slow).mean()

    x["price_vs_ma_fast"] = c / x["ma_fast"] - 1
    x["price_vs_ma_mid"] = c / x["ma_mid"] - 1
    x["price_vs_ma_slow"] = c / x["ma_slow"] - 1

    delta = c.diff()
    gain = delta.clip(lower=0).rolling(rsi_window).mean()
    loss = (-delta.clip(upper=0)).rolling(rsi_window).mean()
    rs = gain / loss.replace(0, np.nan)
    x["rsi"] = 100 - 100 / (1 + rs)

    ema12 = c.ewm(span=12, adjust=False).mean()
    ema26 = c.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False).mean()
    x["macd_hist"] = macd - signal

    x["volume_ratio"] = v / v.rolling(20).mean()

    x["ret_1d"] = c.pct_change()
    x["ret_20d"] = c.pct_change(20)
    x["ret_60d"] = c.pct_change(60)

    x["volatility"] = (
        x["ret_1d"].rolling(vol_window).std() * np.sqrt(252)
    )

    rolling_peak = c.rolling(dd_window).max()
    x["drawdown"] = c / rolling_peak - 1

    # 相对强弱：与沪深300比较
    return x


def merge_benchmark(stock, benchmark):
    b = benchmark[["date", "close"]].copy()
    b["benchmark_ret_20d"] = b["close"].pct_change(20)
    b["benchmark_ret_60d"] = b["close"].pct_change(60)

    x = stock.merge(
        b[["date", "benchmark_ret_20d", "benchmark_ret_60d"]],
        on="date",
        how="left"
    )

    x["relative_20d"] = x["ret_20d"] - x["benchmark_ret_20d"]
    x["relative_60d"] = x["ret_60d"] - x["benchmark_ret_60d"]

    return x


# ----------------------------
# JAE历史评分
# ----------------------------

def technical_score(df):
    s1 = norm(df["price_vs_ma_fast"], -0.15, 0.15)
    s2 = norm(df["price_vs_ma_mid"], -0.20, 0.20)
    s3 = norm(df["price_vs_ma_slow"], -0.25, 0.25)

    rsi = df["rsi"].values
    rsi_score = np.where(
        ~np.isfinite(rsi), 50,
        np.where(
            (rsi >= 45) & (rsi <= 65), 85,
            np.where(
                ((rsi >= 35) & (rsi < 45)) |
                ((rsi > 65) & (rsi <= 75)), 60,
                np.where(rsi < 30, 35, 20)
            )
        )
    )

    macd = norm(df["macd_hist"], -2, 2)
    volume = df["volume_ratio"].values
    volume_score = np.where(
        ~np.isfinite(volume), 50,
        np.where(
            (volume >= 1) & (volume <= 2.5), 85,
            np.where(volume < .7, 45,
                     np.where(volume > 3, 35, 65))
        )
    )

    return (
        .20*s1 +
        .20*s2 +
        .20*s3 +
        .15*rsi_score +
        .15*macd +
        .10*volume_score
    )


def historical_score(df,
                     fundamental_proxy_weight=0.20,
                     valuation_weight=0.15,
                     cycle_weight=0.20,
                     money_weight=0.15,
                     technical_weight=0.15,
                     red_team_weight=0.15):

    """
    纯历史行情版本。
    由于没有带发布日期的财务历史数据，本版本用：
      Fundamental Proxy = 中长期趋势 + 60日相对强弱
      Valuation Proxy    = 反转/回撤状态
      Cycle Proxy        = 20/60日动量 + 相对强弱
      Money Proxy        = 成交量 + 短期动量
    这些是“代理因子”，不是财务事实。

    v1.5可通过历史财报CSV替换代理因子。
    """

    x = df.copy()

    technical = technical_score(x)

    fundamental_proxy = (
        .55 * norm(x["price_vs_ma_slow"], -.25, .25) +
        .45 * norm(x["relative_60d"], -.20, .20)
    )

    valuation_proxy = (
        .60 * inv_norm(x["drawdown"].abs(), .35, .70) +
        .40 * norm(-x["ret_20d"], -.15, .15)
    )

    cycle_proxy = (
        .55 * norm(x["ret_60d"], -.30, .30) +
        .45 * norm(x["relative_60d"], -.20, .20)
    )

    money_proxy = (
        .55 * norm(x["volume_ratio"], .5, 2.5) +
        .45 * norm(x["ret_20d"], -.20, .20)
    )

    red_team = (
        .60 * inv_norm(x["volatility"], .20, .80) +
        .40 * inv_norm(x["drawdown"].abs(), .10, .50)
    )

    total = (
        fundamental_proxy_weight * fundamental_proxy +
        valuation_weight * valuation_proxy +
        cycle_weight * cycle_proxy +
        money_weight * money_proxy +
        technical_weight * technical +
        red_team_weight * red_team
    )

    x["fundamental_score"] = fundamental_proxy
    x["valuation_score"] = valuation_proxy
    x["cycle_score"] = cycle_proxy
    x["money_score"] = money_proxy
    x["technical_score"] = technical
    x["red_team_score"] = red_team
    x["JAE_score"] = total

    return x


# ----------------------------
# 信号与回测
# ----------------------------

def generate_signals(df, threshold=70, hold_days=20,
                     entry_lag=1, stop_loss=None):

    x = df.copy()

    # 信号只在当日收盘后形成；实际收益从下一交易日开始。
    x["signal"] = (x["JAE_score"] >= threshold).astype(int)

    # 下一交易日收盘收益作为统一、可复现的成交近似。
    x["forward_return"] = x["close"].shift(-entry_lag-hold_days) / \
                          x["close"].shift(-entry_lag) - 1

    # 下一交易日起的路径，用于计算持有期最大回撤。
    future_returns = []
    n = len(x)

    for i in range(n):
        start = i + entry_lag
        end = min(start + hold_days, n)
        if start >= n:
            future_returns.append(np.nan)
            continue

        prices = x["close"].iloc[start:end].values
        if len(prices) == 0:
            future_returns.append(np.nan)
            continue

        entry = prices[0]
        path = prices / entry - 1
        future_returns.append(float(path.min()))

    x["trade_max_drawdown"] = future_returns

    # 停损仅用于记录压力测试，不修改基础收益，避免参数混杂。
    if stop_loss is not None:
        x["stop_loss_hit"] = x["trade_max_drawdown"] <= -abs(stop_loss)
    else:
        x["stop_loss_hit"] = False

    return x


def trade_metrics(df):
    trades = df.loc[
        (df["signal"] == 1) &
        df["forward_return"].notna()
    ].copy()

    if trades.empty:
        return {
            "signals": 0,
            "win_rate": np.nan,
            "avg_return": np.nan,
            "median_return": np.nan,
            "best_return": np.nan,
            "worst_return": np.nan,
            "avg_trade_max_dd": np.nan,
            "hit_rate_5pct": np.nan,
            "hit_rate_10pct": np.nan,
        }

    r = trades["forward_return"]
    return {
        "signals": len(trades),
        "win_rate": float((r > 0).mean()),
        "avg_return": float(r.mean()),
        "median_return": float(r.median()),
        "best_return": float(r.max()),
        "worst_return": float(r.min()),
        "avg_trade_max_dd": float(trades["trade_max_drawdown"].mean()),
        "hit_rate_5pct": float((r >= .05).mean()),
        "hit_rate_10pct": float((r >= .10).mean()),
    }


def portfolio_backtest(all_data, threshold=70, hold_days=20,
                       max_positions=3):

    """
    简化等权组合回测：
    每日从当日已产生信号的股票中选择JAE最高的max_positions。
    持有期为hold_days。
    为避免重叠仓位过度复杂，采用“每日信号组合”版本：
    当日收盘评分，下一交易日开始持有；
    组合每日按当日可见信号更新。
    """

    panel = []
    for code, df in all_data.items():
        x = df.copy()
        x["code"] = code
        x["signal"] = x["JAE_score"] >= threshold
        panel.append(x[["date", "code", "close", "JAE_score", "signal"]])

    panel = pd.concat(panel).sort_values(["date", "JAE_score"], ascending=[True, False])

    dates = sorted(panel["date"].dropna().unique())
    daily = []

    for d in dates:
        day = panel[panel["date"] == d]
        candidates = day[day["signal"]].sort_values("JAE_score", ascending=False).head(max_positions)

        if candidates.empty:
            daily.append({"date": d, "portfolio_return": 0.0, "positions": 0})
            continue

        # 用下一日收益；最后一天没有下一日则跳过。
        rets = []
        for _, row in candidates.iterrows():
            code = row["code"]
            df = all_data[code]
            idxs = df.index[df["date"] == d].tolist()
            if not idxs:
                continue
            i = idxs[0]
            if i + 1 >= len(df):
                continue
            r = df.iloc[i+1]["close"] / df.iloc[i]["close"] - 1
            rets.append(r)

        daily.append({
            "date": d,
            "portfolio_return": np.mean(rets) if rets else 0.0,
            "positions": len(rets)
        })

    daily = pd.DataFrame(daily)
    daily["equity"] = (1 + daily["portfolio_return"]).cumprod()

    return daily


# ----------------------------
# 参数敏感性
# ----------------------------

def parameter_sensitivity(all_data,
                          thresholds=(60, 65, 70, 75, 80),
                          holds=(5, 10, 20, 40),
                          fast_windows=(10, 20, 30)):

    records = []

    for threshold, hold, fast in itertools.product(
        thresholds, holds, fast_windows
    ):
        per_stock = []

        for code, raw in all_data.items():
            x = raw.copy()

            # 重新计算快速均线，模拟参数变化。
            x["ma_fast"] = x["close"].rolling(fast).mean()
            x["price_vs_ma_fast"] = x["close"] / x["ma_fast"] - 1

            x["JAE_score"] = historical_score(
                x
            )["JAE_score"]

            x = generate_signals(
                x,
                threshold=threshold,
                hold_days=hold
            )

            m = trade_metrics(x)

            if m["signals"] > 0:
                per_stock.append(m)

        if not per_stock:
            continue

        tmp = pd.DataFrame(per_stock)

        records.append({
            "threshold": threshold,
            "hold_days": hold,
            "fast_ma": fast,
            "signals": int(tmp["signals"].sum()),
            "win_rate": tmp["win_rate"].mean(),
            "avg_return": tmp["avg_return"].mean(),
            "median_return": tmp["median_return"].mean(),
            "worst_return": tmp["worst_return"].min(),
            "avg_trade_max_dd": tmp["avg_trade_max_dd"].mean(),
        })

    return pd.DataFrame(records)


# ----------------------------
# 主程序
# ----------------------------

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("--start", default="20230101")
    parser.add_argument("--end", default=pd.Timestamp.today().strftime("%Y%m%d"))

    parser.add_argument(
        "--thresholds",
        default="60,65,70,75,80",
        help="JAE信号阈值"
    )

    parser.add_argument(
        "--holds",
        default="5,10,20,40",
        help="持有天数"
    )

    parser.add_argument(
        "--out",
        default="jae_fin_v1_4_backtest.xlsx"
    )

    args = parser.parse_args()

    ak = load_akshare()

    thresholds = tuple(
        float(x) for x in args.thresholds.split(",")
    )
    holds = tuple(
        int(x) for x in args.holds.split(",")
    )

    print("=" * 70)
    print("JAE-FIN v1.4 | HISTORICAL BACKTEST ENGINE")
    print("=" * 70)

    # 沪深300基准
    benchmark = ak.index_zh_a_hist(
        symbol="000300",
        period="daily",
        start_date=args.start,
        end_date=args.end
    )

    benchmark = benchmark.rename(
        columns={"日期": "date", "收盘": "close"}
    )
    benchmark["date"] = pd.to_datetime(benchmark["date"])
    benchmark["close"] = pd.to_numeric(benchmark["close"], errors="coerce")
    benchmark = benchmark.sort_values("date")

    all_data = {}
    signal_results = []

    for code, (name, sector) in WATCHLIST.items():

        print(f"[下载] {code} {name}")

        try:
            df = get_history(
                ak,
                code,
                args.start,
                args.end
            )

            if df.empty:
                print("  无数据")
                continue

            df = build_features(df)

            df = merge_benchmark(
                df,
                benchmark
            )

            df = historical_score(df)

            df["code"] = code
            df["name"] = name
            df["sector"] = sector

            all_data[code] = df

            # 默认阈值70、20日持有
            x = generate_signals(
                df,
                threshold=70,
                hold_days=20
            )

            m = trade_metrics(x)

            signal_results.append({
                "code": code,
                "name": name,
                "sector": sector,
                **m
            })

        except Exception as e:
            print("  失败：", e)

    if not all_data:
        raise SystemExit("没有成功获取股票数据。")

    signal_df = pd.DataFrame(signal_results)

    # 每只股票历史评分样本
    score_panel = pd.concat(
        [
            df[
                [
                    "date", "code", "name", "sector",
                    "JAE_score",
                    "fundamental_score",
                    "valuation_score",
                    "cycle_score",
                    "money_score",
                    "technical_score",
                    "red_team_score"
                ]
            ]
            for df in all_data.values()
        ],
        ignore_index=True
    )

    # 组合回测
    portfolio = portfolio_backtest(
        all_data,
        threshold=70,
        max_positions=3
    )

    portfolio_return = (
        portfolio["equity"].iloc[-1] - 1
    )

    portfolio_mdd = max_drawdown(
        portfolio["equity"]
    )

    portfolio_cagr = annualized_return(
        portfolio["equity"]
    )

    portfolio_sharpe = sharpe(
        portfolio["portfolio_return"]
    )

    portfolio_summary = pd.DataFrame([{
        "strategy": "JAE-FIN threshold=70 top3",
        "total_return": portfolio_return,
        "annualized_return": portfolio_cagr,
        "max_drawdown": portfolio_mdd,
        "sharpe": portfolio_sharpe,
        "days": len(portfolio)
    }])

    # 参数敏感性
    sensitivity = parameter_sensitivity(
        all_data,
        thresholds=thresholds,
        holds=holds,
        fast_windows=(10, 20, 30)
    )

    # 参数稳定性指标：
    # 不寻找“最赚钱参数”，而寻找较稳定区域。
    if not sensitivity.empty:
        sensitivity["return_minus_drawdown"] = (
            sensitivity["avg_return"] +
            sensitivity["avg_trade_max_dd"]
        )

        sensitivity["robust_rank"] = (
            sensitivity["win_rate"].rank(pct=True) * .4 +
            sensitivity["return_minus_drawdown"].rank(pct=True) * .6
        )

        sensitivity = sensitivity.sort_values(
            "robust_rank",
            ascending=False
        )

    # 基准收益
    benchmark = benchmark.dropna(subset=["close"]).copy()
    benchmark["equity"] = benchmark["close"] / benchmark["close"].iloc[0]

    benchmark_summary = pd.DataFrame([{
        "benchmark": "沪深300",
        "total_return": benchmark["equity"].iloc[-1] - 1,
        "annualized_return": annualized_return(benchmark["equity"]),
        "max_drawdown": max_drawdown(benchmark["equity"]),
        "sharpe": sharpe(benchmark["close"].pct_change())
    }])

    # 输出Excel
    with pd.ExcelWriter(
        args.out,
        engine="openpyxl"
    ) as writer:

        signal_df.to_excel(
            writer,
            sheet_name="信号收益",
            index=False
        )

        score_panel.to_excel(
            writer,
            sheet_name="历史评分",
            index=False
        )

        portfolio.to_excel(
            writer,
            sheet_name="组合回测",
            index=False
        )

        portfolio_summary.to_excel(
            writer,
            sheet_name="策略摘要",
            index=False
        )

        benchmark_summary.to_excel(
            writer,
            sheet_name="基准",
            index=False
        )

        sensitivity.to_excel(
            writer,
            sheet_name="参数敏感性",
            index=False
        )

    # 控制台摘要
    print("\n" + "=" * 70)
    print("JAE-FIN v1.4 回测完成")
    print("=" * 70)

    print("\n【个股信号收益】")
    print(
        signal_df[
            [
                "code",
                "name",
                "signals",
                "win_rate",
                "avg_return",
                "median_return",
                "worst_return",
                "avg_trade_max_dd"
            ]
        ].to_string(index=False)
    )

    print("\n【组合回测】")
    print(
        portfolio_summary.to_string(index=False)
    )

    print("\n【沪深300】")
    print(
        benchmark_summary.to_string(index=False)
    )

    print("\n【参数敏感性 Top 10】")
    if sensitivity.empty:
        print("没有足够的参数组合结果。")
    else:
        print(
            sensitivity.head(10).to_string(index=False)
        )

    print(f"\n输出文件：{args.out}")

    print("\n重要说明：")
    print("1. v1.4的历史基本面/估值使用行情代理因子，避免未来财报倒灌。")
    print("2. 信号形成于当日收盘，收益从下一交易日开始计算。")
    print("3. 参数敏感性不是为了挑选历史最优参数，而是检查模型是否稳定。")
    print("4. 真正接入带发布日期的历史财报后，v1.5才能形成完整六因子历史回测。")


if __name__ == "__main__":
    main()