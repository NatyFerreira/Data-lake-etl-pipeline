# Data Lake ETL Pipeline

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![License](https://img.shields.io/badge/License-Academic-lightgrey)

End-to-end ETL pipeline implementing a three-zone data lake architecture (Raw → Processed → Curated) over two heterogeneous data sources (CSV and JSON).  
Built as an introduction to data engineering fundamentals (Campus Numérique in the Alps — Data Engineer & AI, RNCP Level 7, 2026).

---

## Project Structure

```
Data-lake-etl-pipeline/
├── pipeline.py                         # Full ETL pipeline (extract, transform, enrich, quality, aggregate)
├── data/
│   ├── raw/
│   │   ├── business.csv                # Simulated business data (raw, unmodified)
│   │   └── sensor.json                 # Simulated sensor data (raw, unmodified)
│   ├── processed/
│   │   ├── normalized_events.json      # Unified schema output (business + sensor merged)
│   │   ├── metadata.json               # Pipeline execution metadata
│   │   └── quality_report.json         # Data quality validation results
│   └── curated/
│       └── hourly_temperature.json     # Aggregated analytical output (ready for BI)
└── README.md
```

---

## Data Lake Architecture

The pipeline follows a standard three-zone data lake pattern:

```
data/raw/          ←  unmodified source files (business.csv, sensor.json)
      │
      ▼  Extract + Normalize
data/processed/    ←  unified schema, metadata, quality report
      │
      ▼  Aggregate
data/curated/      ←  analytical products ready for dashboards or reporting
```

This separation ensures clarity, reproducibility, and proper governance of the data lifecycle.

---

## Technology Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.11 |
| Data formats | CSV, JSON |
| Architecture | Three-zone data lake (Raw / Processed / Curated) |
| Timezone handling | Europe/Paris (pytz) |

---

## Installation

```bash
git clone https://github.com/NatyFerreira/Data-lake-etl-pipeline.git
cd Data-lake-etl-pipeline
python3 pipeline.py
```

No additional dependencies beyond the Python standard library and pytz.

---

## Pipeline Steps

### 1. Ingestion (Extract)

Loads raw files from `data/raw/` without applying any transformation:

```python
load_business_csv()   # reads business.csv
load_sensor_json()    # reads sensor.json
```

### 2. Normalisation (Transform)

Converts both sources into a common event schema:

| Field | Description |
|-------|-------------|
| `event_time` | Timestamp of the event |
| `entity_id` | Identifier of the entity (business unit or sensor) |
| `metric` | Metric name |
| `value` | Measured value |
| `unit` | Unit of measurement |
| `source` | Origin of the record (`business` or `sensor`) |

The unified schema allows both datasets to be merged and processed consistently downstream.

### 3. Enrichment & Metadata

`build_metadata()` generates a traceability record per pipeline run:

- Processing timestamp (Europe/Paris timezone)
- Number of normalised records
- List of input sources and record counts
- Description of data lake zones

### 4. Data Quality Checks

`build_quality_report()` validates sensor data and flags:

- Events with `status == "warning"`
- Unusually high or low temperature readings
- Records with missing `status` fields
- Examples of problematic records

Output: `data/processed/quality_report.json`

### 5. Aggregation (Curated Layer)

`aggregate_hourly_temperature()` computes hourly averages of temperature readings and saves the result to `data/curated/hourly_temperature.json` — ready for dashboards, visualisation tools, or further analysis.

---

## Outputs

| File | Zone | Description |
|------|------|-------------|
| `normalized_events.json` | Processed | Unified schema — business + sensor events merged |
| `metadata.json` | Processed | Pipeline execution metadata for traceability |
| `quality_report.json` | Processed | Data quality validation results |
| `hourly_temperature.json` | Curated | Hourly temperature aggregates (analytical output) |

---

## Author

**Natália Helen Ferreira**  
PhD in Biological Chemistry | Data Engineer & AI (RNCP Level 7, in progress)  
[LinkedIn](https://linkedin.com/in/ferreiranh) · [GitHub](https://github.com/NatyFerreira)

---

## License

Academic project — free to use for educational purposes.
