import csv
import math
import random
import uuid
from datetime import date, datetime, timedelta
from pathlib import Path

import numpy as np
import yaml


def _convert_dates(obj):
    if isinstance(obj, dict):
        return {k: _convert_dates(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_convert_dates(v) for v in obj]
    if isinstance(obj, (datetime, date)):
        return obj.strftime("%Y-%m-%d")
    return obj


def load_config(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return _convert_dates(yaml.safe_load(f))


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
    return all_rows, fieldnames


def find_indices_by_dim(rows, dim, value):
    return [i for i, r in enumerate(rows) if r.get(dim) == value]


def inject_spike(rows, indices, date_str, magnitude, direction, fieldnames):
    sign = 1 if direction == "positive" else -1
    for i in indices:
        row = rows[i]
        if row["date"] == date_str:
            row["amount"] = str(round(float(row["amount"]) * (1 + sign * magnitude), 2))
            row["cost"] = str(round(float(row["cost"]) * (1 + sign * magnitude * 0.9), 2))
            row["margin"] = str(round(float(row["amount"]) - float(row["cost"]), 2))
            row["description"] = row.get("description", "") + " [ANOMALY: spike]"
    return rows


def inject_level_shift(rows, indices, start_date, magnitude, fieldnames):
    for i in indices:
        row = rows[i]
        if row["date"] >= start_date:
            row["amount"] = str(round(float(row["amount"]) * (1 + magnitude), 2))
            row["cost"] = str(round(float(row["cost"]) * (1 + magnitude * 0.9), 2))
            row["margin"] = str(round(float(row["amount"]) - float(row["cost"]), 2))
            if "[ANOMALY:" not in row.get("description", ""):
                row["description"] = row.get("description", "") + " [ANOMALY: level_shift]"
    return rows


def inject_trend_break(rows, indices, break_date, new_slope, base_slope, fieldnames):
    for i in indices:
        row = rows[i]
        if row["date"] >= break_date:
            d = datetime.strptime(row["date"], "%Y-%m-%d")
            bd = datetime.strptime(break_date, "%Y-%m-%d")
            days_since = (d - bd).days
            if days_since > 0:
                adjustment = 1 + (new_slope - base_slope) * (days_since / 365.0)
                adjustment = max(0.5, min(2.0, adjustment))
                row["amount"] = str(round(float(row["amount"]) * adjustment, 2))
                row["cost"] = str(round(float(row["cost"]) * adjustment * 0.95, 2))
                row["margin"] = str(round(float(row["amount"]) - float(row["cost"]), 2))
                if "[ANOMALY:" not in row.get("description", ""):
                    row["description"] = row.get("description", "") + " [ANOMALY: trend_break]"
    return rows


def inject_dimension_local(rows, indices, dim, target_value, magnitude, compensation, fieldnames):
    target_indices = [i for i in indices if rows[i].get(dim) == target_value]
    other_indices = [i for i in indices if i not in target_indices]

    for i in target_indices:
        row = rows[i]
        row["amount"] = str(round(float(row["amount"]) * (1 - magnitude), 2))
        row["cost"] = str(round(float(row["cost"]) * (1 - magnitude * 0.8), 2))
        row["margin"] = str(round(float(row["amount"]) - float(row["cost"]), 2))
        if "[ANOMALY:" not in row.get("description", ""):
            row["description"] = row.get("description", "") + " [ANOMALY: dimension_local]"

    if compensation:
        for i in other_indices:
            row = rows[i]
            row["amount"] = str(round(float(row["amount"]) * (1 + 0.05), 2))
            row["cost"] = str(round(float(row["cost"]) * (1 + 0.03), 2))
            row["margin"] = str(round(float(row["amount"]) - float(row["cost"]), 2))
            if "[ANOMALY:" not in row.get("description", ""):
                row["description"] = row.get("description", "") + " [ANOMALY: dimension_local_comp]"

    return rows


def inject(config_path: str, base_path: str, output_path: str, seed: int = 42):
    config = load_config(Path(config_path))
    base_config = load_config(Path(base_path).parent.parent / "config" / "base_trend.yaml")
    with open(base_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames

    # merge dimensions from base config
    config["dimensions"] = base_config.get("dimensions", {})

    rng = random.Random(seed)
    np.random.seed(seed)

    scenario_id = 0
    labels = []
    scenarios_cfg = config.get("scenarios", {})

    # Spike/Dip
    if scenarios_cfg.get("spike_dip", {}).get("enabled"):
        for mag in scenarios_cfg["spike_dip"]["magnitudes"]:
            for dur in scenarios_cfg["spike_dip"]["duration_days"]:
                for dim in scenarios_cfg["spike_dip"]["affected_dimensions"]:
                    values = [v for v in config["dimensions"].get(dim + "s", [])]
                    for direction in scenarios_cfg["spike_dip"]["directions"]:
                        for target_value in values[:2]:
                            scenario_id += 1
                            sid = f"A1_spike_{scenario_id}_{mag}sigma_{direction}"
                            date_str = "2024-06-15"
                            candidate_indices = find_indices_by_dim(rows, dim, target_value)
                            date_indices = [i for i in candidate_indices if rows[i]["date"] == date_str]
                            sample_size = min(len(date_indices), rng.randint(5, 15))
                            if sample_size > 0:
                                sampled = rng.sample(date_indices, sample_size)
                                inject_spike(rows, sampled, date_str, mag * 0.1, direction, fieldnames)
                                affected = [i for i in sampled if rows[i]["date"] == date_str]
                                labels.append({
                                    "scenario_id": sid,
                                    "anomaly_type": "spike",
                                    "magnitude": mag,
                                    "dimension": f"{dim}={target_value}",
                                    "date_start": date_str,
                                    "date_end": date_str,
                                    "affected_rows": len(affected),
                                    "ground_truth_value": str(sum(float(rows[i]["amount"]) for i in affected)),
                                    "expected_detection": "TRUE",
                                })

    # Level Shift
    if scenarios_cfg.get("level_shift", {}).get("enabled"):
        for mag in scenarios_cfg["level_shift"]["magnitudes"]:
            for start_date in scenarios_cfg["level_shift"]["start_dates"][:2]:
                for dim in scenarios_cfg["level_shift"]["affected_dimensions"]:
                    values = [v for v in config["dimensions"].get(dim + "s", [])]
                    for target_value in values[:2]:
                        scenario_id += 1
                        sid = f"A2_level_{scenario_id}_{int(mag*100)}pct_{target_value}"
                        candidate_indices = find_indices_by_dim(rows, dim, target_value)
                        eligible = [i for i in candidate_indices if rows[i]["date"] >= start_date]
                        sample_size = min(len(eligible), rng.randint(20, 50))
                        if sample_size > 0:
                            sampled = rng.sample(eligible, sample_size)
                            inject_level_shift(rows, sampled, start_date, mag, fieldnames)
                            affected = [i for i in sampled if rows[i]["date"] >= start_date]
                            labels.append({
                                "scenario_id": sid,
                                "anomaly_type": "level_shift",
                                "magnitude": mag,
                                "dimension": f"{dim}={target_value}",
                                "date_start": start_date,
                                "date_end": "2024-12-31",
                                "affected_rows": len(affected),
                                "ground_truth_value": str(sum(float(rows[i]["amount"]) for i in affected)),
                                "expected_detection": "TRUE",
                            })

    # Trend Break
    if scenarios_cfg.get("trend_break", {}).get("enabled"):
        for break_date in scenarios_cfg["trend_break"]["break_dates"][:2]:
            for new_slope in scenarios_cfg["trend_break"]["new_slopes"][:3]:
                for dim in scenarios_cfg["trend_break"]["affected_dimensions"]:
                    values = [v for v in config["dimensions"].get(dim + "s", [])]
                    for target_value in values[:2]:
                        scenario_id += 1
                        sid = f"A3_trend_{scenario_id}_{new_slope}_{target_value}"
                        candidate_indices = find_indices_by_dim(rows, dim, target_value)
                        eligible = [i for i in candidate_indices if rows[i]["date"] >= break_date]
                        sample_size = min(len(eligible), rng.randint(20, 50))
                        if sample_size > 0:
                            sampled = rng.sample(eligible, sample_size)
                            inject_trend_break(rows, sampled, break_date, new_slope, 0.01, fieldnames)
                            affected = [i for i in sampled if rows[i]["date"] >= break_date]
                            labels.append({
                                "scenario_id": sid,
                                "anomaly_type": "trend_break",
                                "magnitude": new_slope,
                                "dimension": f"{dim}={target_value}",
                                "date_start": break_date,
                                "date_end": "2024-12-31",
                                "affected_rows": len(affected),
                                "ground_truth_value": str(sum(float(rows[i]["amount"]) for i in affected)),
                                "expected_detection": "TRUE",
                            })

    # Dimension-Local
    if scenarios_cfg.get("dimension_local", {}).get("enabled"):
        for mag in scenarios_cfg["dimension_local"]["magnitudes"]:
            for dim in scenarios_cfg["dimension_local"]["affected_dimensions"]:
                values = [v for v in config["dimensions"].get(dim + "s", [])]
                for target_value in values[:2]:
                    scenario_id += 1
                    sid = f"A4_dimlocal_{scenario_id}_{int(mag*100)}pct_{target_value}"
                    candidate_indices = find_indices_by_dim(rows, dim, target_value)
                    sample_size = min(len(candidate_indices), rng.randint(10, 30))
                    if sample_size > 0:
                        sampled = rng.sample(candidate_indices, sample_size)
                        inject_dimension_local(rows, sampled, dim, target_value, mag,
                                               scenarios_cfg["dimension_local"].get("compensation", {}).get("enabled", False),
                                               fieldnames)
                        affected = [i for i in sampled]
                        labels.append({
                            "scenario_id": sid,
                            "anomaly_type": "dimension_local",
                            "magnitude": mag,
                            "dimension": f"{dim}={target_value}",
                            "date_start": "2024-09-01",
                            "date_end": "2024-12-31",
                            "affected_rows": len(affected),
                            "ground_truth_value": str(sum(float(rows[i]["amount"]) for i in affected)),
                            "expected_detection": "TRUE",
                        })

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    label_path = Path(output_path).parent / "labels.csv"
    if labels:
        with open(label_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(labels[0].keys()))
            writer.writeheader()
            writer.writerows(labels)

    print(f"Injected {scenario_id} scenarios -> {output_path}")
    print(f"Labels saved -> {label_path}")
    return rows, labels


def verify_labels(labels_path: Path, output_path: Path):
    with open(labels_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        labels = list(reader)
        fields = reader.fieldnames

    verified = []
    for row in labels:
        if row.get("scenario_id") and row.get("anomaly_type") and int(row.get("affected_rows", 0)) > 0:
            row["verified"] = "TRUE"
            verified.append(row)
        else:
            row["verified"] = "FALSE"

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields + ["verified"])
        writer.writeheader()
        writer.writerows(verified)

    print(f"Verified labels: {len(verified)}/{len(labels)} passed -> {output_path}")
    return verified


def main():
    base_dir = Path(__file__).resolve().parent
    config_dir = base_dir / "config"
    output_dir = base_dir / "output"
    output_dir.mkdir(exist_ok=True)

    print("=== Stage 1: Generate base ledger ===")
    generate(str(config_dir / "base_trend.yaml"), str(output_dir / "ledger_base.csv"))

    print("=== Stage 2: Inject anomalies ===")
    inject(
        str(config_dir / "anomaly_scenarios.yaml"),
        str(output_dir / "ledger_base.csv"),
        str(output_dir / "ledger_anomaly.csv"),
        seed=42,
    )

    print("=== Stage 3: Verify labels ===")
    verify_labels(output_dir / "labels.csv", output_dir / "labels_verified.csv")

    print("=== Pipeline complete ===")
    print(f"Output directory: {output_dir}")
    for f in sorted(output_dir.iterdir()):
        print(f"  {f.name}: {f.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
