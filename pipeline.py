import csv
import json
from collections import defaultdict
from datetime import datetime
import pytz
from pathlib import Path

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
CURATED_DIR = Path("data/curated")

def load_business_csv(path: Path):
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))

def load_sensor_json(path: Path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)

def normalize_business(rows):
    normalized = []
    for row in rows:
        normalized.append({
            "source": "business",
            "event_time": row["event_time"],
            "entity_id": row["customer_id"],
            "site": row["site"],
            "metric": row["metric_type"],
            "value": float(row["value"]),
            "unit": row["unit"],
        })
    return normalized

def normalize_sensor(rows):
    normalized = []
    for row in rows:
        normalized.append({
            "source": "sensor",
            "event_time": row["timestamp"],
            "entity_id": row["device_id"],
            "site": "unknown",
            "metric": "temperature_c",
            "value": float(row["temperature_c"]),
            "unit": "celsius",
            "status": row.get("status", "unknown"),
        })
    return normalized

def save_json(data, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def build_metadata(business_rows, sensor_rows):
    return {
        "generated_at": datetime.now(pytz.timezone("Europe/Paris")).isoformat(),
        "sources": [
            {"name": "business.csv", "format": "csv", "records": len(business_rows)},
            {"name": "sensor.json", "format": "json", "records": len(sensor_rows)},
        ],
        "zones": ["raw", "processed", "curated"],
    }

def aggregate_hourly_temperature(rows):
    buckets = defaultdict(list)
    for row in rows:
        if row["metric"] != "temperature_c":
            continue
        dt = datetime.fromisoformat(row["event_time"])
        hour_key = dt.replace(minute=0, second=0, microsecond=0).isoformat()
        buckets[hour_key].append(row["value"])

    output = []
    for hour_key, values in sorted(buckets.items()):
        output.append({
            "hour": hour_key,
            "avg_temperature_c": round(sum(values) / len(values), 2),
            "samples": len(values),
        })
    return output

def build_quality_report(sensor_rows):
    warnings = [row for row in sensor_rows if row.get("status") == "warning"]
    high_temp = [row for row in sensor_rows if float(row["temperature_c"]) > 28]
    low_temp = [row for row in sensor_rows if float(row["temperature_c"]) < 15]
    return {
        "warning_count": len(warnings),
        "high_temperature_count": len(high_temp),
        "low_temperature_count": len(low_temp),
        "examples": {
            "warning": warnings[:3],
            "high_temperature": high_temp[:3],
            "low_temperature": low_temp[:3],
        },
    }

def main():
    business_rows = load_business_csv(RAW_DIR / "business.csv")
    sensor_rows = load_sensor_json(RAW_DIR / "sensor.json")

    normalized = normalize_business(business_rows) + normalize_sensor(sensor_rows)
    save_json(normalized, PROCESSED_DIR / "normalized_events.json")
    save_json(build_metadata(business_rows, sensor_rows), PROCESSED_DIR / "metadata.json")
    save_json(aggregate_hourly_temperature(normalized), CURATED_DIR / "hourly_temperature.json")
    save_json(build_quality_report(sensor_rows), CURATED_DIR / "quality_report.json")

    print(f"Processed {len(normalized)} normalized events")

if __name__ == "__main__":
    main()
