import csv
import math
import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import yaml


def load_config(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def fourier_series(t, period, amplitude, harmonics=3):
    value = 0.0
    for k in range(1, harmonics + 1):
        value += (amplitude / k) * math.sin(2 * math.pi * k * t / period)
    return value


def compute_trend(date, trend_cfg):
    for seg in trend_cfg["slopes"]:
        start = datetime.strptime(seg["start"], "%Y-%m-%d").date()
        end = datetime.strptime(seg["end"], "%Y-%m-%d").date()
        if start <= date <= end:
            days = (end - start).days
            if days == 0:
                return 0.0
            elapsed = (date - start).days
            return seg["slope"] * elapsed
    return 0.0


def compute_season(date, season_cfg):
    t = date.timetuple().tm_yday
    value = 0.0
    for p in season_cfg.get("periods", []):
        value += fourier_series(t, p["period"], p["amplitude"])
    for h in season_cfg.get("holidays", []):
        hdate = datetime.strptime(h["date"], "%Y-%m-%d").date()
        delta = abs((date - hdate).days)
        if delta <= 3:
            factor = 1 - (delta / 4)
            value += h["effect"] * factor * (1 if h["direction"] == "positive" else -1)
    return value


def compute_base_value(date, config):
    trend = compute_trend(date, config["trend"])
    season = compute_season(date, config["season"])
    noise = np.random.normal(config["noise"]["mean"], config["noise"]["std"])
    return 1 + trend + season + noise


def generate_transactions_for_day(date, config, rng):
    rows = []
    regions = config["dimensions"]["regions"]
    products = config["dimensions"]["products"]
    channels = config["dimensions"]["channels"]
    factors = config["factors"]
    base = config["base_values"]["revenue_base"]

    num_txns = rng.randint(config["transactions_per_day"]["min"], config["transactions_per_day"]["max"])

    for _ in range(num_txns):
        region = rng.choice(regions)
        product = rng.choice(products)
        channel = rng.choice(channels)

        base_val = compute_base_value(date, config)
        region_factor = factors["region"].get(region, 1.0)
        product_factor = factors["product"].get(product, 1.0)
        channel_factor = factors["channel"].get(channel, 1.0)

        amount = base * base_val * region_factor * product_factor * channel_factor
        amount = max(100.0, round(amount, 2))

        cost = round(amount * config["base_values"]["cost_ratio"] * rng.uniform(0.9, 1.1), 2)
        margin = round(amount - cost, 2)

        txn_type = rng.choices(
            ["Invoice", "Payment", "Credit Memo", "Estimate", "Sales Receipt"],
            weights=[0.35, 0.30, 0.10, 0.15, 0.10],
            k=1
        )[0]

        rows.append({
            "transaction_id": str(uuid.uuid4())[:8],
            "date": date.isoformat(),
            "region": region,
            "product": product,
            "channel": channel,
            "transaction_type": txn_type,
            "amount": amount,
            "cost": cost,
            "margin": margin,
            "customer_id": f"CUST-{rng.randint(1000, 9999)}",
            "vendor_id": f"VEND-{rng.randint(1000, 9999)}",
            "description": f"{txn_type} - {product} - {region}",
        })
    return rows


def generate(config_path: str, output_path: str):
    config = load_config(Path(config_path))
    rng = random.Random(config.get("seed", 42))
    np.random.seed(config.get("seed", 42))

    start = datetime.strptime(config["time"]["start"], "%Y-%m-%d").date()
    end = datetime.strptime(config["time"]["end"], "%Y-%m-%d").date()
    freq = config["time"]["freq"]

    dates = []
    current = start
    while current <= end:
        dates.append(current)
        if freq == "D":
            current += timedelta(days=1)
        elif freq == "M":
            current = (current.replace(day=28) + timedelta(days=4)).replace(day=1)
        else:
            current += timedelta(days=1)

    all_rows = []
    for date in dates:
        all_rows.extend(generate_transactions_for_day(date, config, rng))

    fieldnames = config["output"]["columns"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"Generated {len(all_rows)} rows -> {output_path}")
    return all_rows


if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent.parent
    config_path = base_dir / "config" / "base_trend.yaml"
    output_path = base_dir / "output" / "ledger_base.csv"
    generate(str(config_path), str(output_path))
