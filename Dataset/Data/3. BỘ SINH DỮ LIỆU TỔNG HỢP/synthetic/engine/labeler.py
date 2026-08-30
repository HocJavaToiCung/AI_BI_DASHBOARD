import csv
from pathlib import Path


def load_csv(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader), reader.fieldnames


def save_csv(path: Path, rows, fieldnames):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def verify_labels(labels_path: Path, output_path: Path):
    labels, fields = load_csv(labels_path)

    verified = []
    for row in labels:
        if row.get("scenario_id") and row.get("anomaly_type") and int(row.get("affected_rows", 0)) > 0:
            row["verified"] = "TRUE"
            verified.append(row)
        else:
            row["verified"] = "FALSE"

    save_csv(output_path, verified, fields + ["verified"])
    print(f"Verified labels: {len(verified)}/{len(labels)} passed -> {output_path}")
    return verified


if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent.parent
    verify_labels(base_dir / "output" / "labels.csv", base_dir / "output" / "labels_verified.csv")
