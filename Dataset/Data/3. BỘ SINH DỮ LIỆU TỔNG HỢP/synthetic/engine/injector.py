import csv
import math
import random
from datetime import datetime
from pathlib import Path

import numpy as np
import yaml


def load_config(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_csv(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader), reader.fieldnames


def save_csv(path: Path, rows, fieldnames):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


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


def inject_dimension_local(rows, indices, target_dim, target_value, magnitude, compensation, fieldnames):
    target_indices = [i for i in indices if rows[i].get(target_dim.split("=")[0]) == target_value.split("=")[1]]
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


def run(base_path: str, output_path: str, config_path: str, seed: int = 42):
    config = load_config(Path(config_path))
    rows, fieldnames = load_csv(Path(base_path))
    rng = random.Random(seed)
    np.random.seed(seed)

    scenario_id = 0
    labels = []

    scenarios_cfg = config.get("scenarios", {})
    global_cfg = config.get("global_settings", {})

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
                            indices = find_indices_by_dim(rows, dim, target_value)
                            if indices:
                                inject_spike(rows, indices[:20], date_str, mag * 0.1, direction, fieldnames)
                                affected = [i for i in indices[:20] if rows[i]["date"] == date_str]
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
                        indices = find_indices_by_dim(rows, dim, target_value)
                        if indices:
                            inject_level_shift(rows, indices[:50], start_date, mag, fieldnames)
                            affected = [i for i in indices[:50] if rows[i]["date"] >= start_date]
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
                        indices = find_indices_by_dim(rows, dim, target_value)
                        if indices:
                            inject_trend_break(rows, indices[:50], break_date, new_slope, 0.01, fieldnames)
                            affected = [i for i in indices[:50] if rows[i]["date"] >= break_date]
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
                    indices = find_indices_by_dim(rows, dim, target_value)
                    if indices:
                        inject_dimension_local(rows, indices[:30], dim, target_value, mag,
                                               scenarios_cfg["dimension_local"].get("compensation", {}).get("enabled", False),
                                               fieldnames)
                        affected = [i for i in indices[:30]]
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

    save_csv(Path(output_path), rows, fieldnames)

    label_path = Path(output_path).parent / "labels.csv"
    if labels:
        with open(label_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(labels[0].keys()))
            writer.writeheader()
            writer.writerows(labels)

    print(f"Injected {scenario_id} scenarios -> {output_path}")
    print(f"Labels saved -> {label_path}")
    return rows, labels


if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent.parent
    run(
        str(base_dir / "output" / "ledger_base.csv"),
        str(base_dir / "output" / "ledger_anomaly.csv"),
        str(base_dir / "config" / "anomaly_scenarios.yaml"),
        seed=42,
    )
