# Source code kit - Introduction à l'écosystème data

## Contenu
- `data/raw/business.csv` : données métier simulées
- `data/raw/sensor.json` : données capteurs simulées
- `pipeline.py` : pipeline d'exemple
- `data/processed/` : sorties intermédiaires
- `data/curated/` : sorties prêtes à être exploitées

## Lancer le pipeline

```bash
cd repo
python3 pipeline.py
```

## Sorties générées
- `data/processed/normalized_events.json`
- `data/processed/metadata.json`
- `data/curated/hourly_temperature.json`
- `data/curated/quality_report.json`

---

# **Data Pipeline Documentation **

## **Overview**
This project implements a complete data pipeline following modern data lake principles.  
It processes two heterogeneous data sources (CSV and JSON), normalizes them into a unified schema, enriches the dataset with metadata, performs data quality checks, and produces analytical outputs ready for visualization or reporting.

The pipeline is structured into three zones:

- **raw** – unmodified source data  
- **processed** – cleaned, normalized, enriched data  
- **curated** – final analytical datasets  

---

## **1. Data Ingestion (Extract)**

The pipeline begins by loading the raw files stored in the `data/raw` directory:

- `load_business_csv()` reads **business.csv**
- `load_sensor_json()` reads **sensor.json**

At this stage, no transformation is applied.  
The goal is simply to ingest the raw data exactly as it was received.

---

## **2. Data Normalization (Transform)**

Because the two sources have different formats and structures, I created two normalization functions:

- `normalize_business()`
- `normalize_sensor()`

Both functions convert their respective inputs into a **common event schema**, including fields such as:

- `event_time`
- `entity_id`
- `metric`
- `value`
- `unit`
- `source`

This unified structure allows the two datasets to be merged and processed consistently.

---

## **3. Enrichment and Metadata**

To ensure traceability and documentation of each pipeline execution, I generate a metadata file using `build_metadata()`.  
This file includes:

- processing timestamp (Europe/Paris timezone)
- number of normalized records
- list of input sources and their record counts
- description of the data lake zones

This enrichment step adds valuable context for auditing and reproducibility.

---

## **4. Data Quality Checks**

The function `build_quality_report()` performs several quality validations on the sensor data:

- detection of events with status `"warning"`
- identification of unusually high or low temperatures
- detection of missing `status` fields
- examples of problematic records

The resulting `quality_report.json` is stored in the **processed** zone, as it represents cleaned and validated information.

---

## **5. Data Lake Zones**

The project follows the standard three‑zone data lake architecture:

### **Raw Zone (`data/raw/`)**
Contains the original files exactly as received:
- `business.csv`
- `sensor.json`

### **Processed Zone (`data/processed/`)**
Contains cleaned, normalized, and enriched datasets:
- `normalized_events.json`
- `metadata.json`
- `quality_report.json`

### **Curated Zone (`data/curated/`)**
Contains final analytical products ready for BI or visualization:
- `hourly_temperature.json`

This separation ensures clarity, reproducibility, and proper governance of the data lifecycle.

---

## **6. Analytical Product (Curated Layer)**

The function `aggregate_hourly_temperature()` computes hourly averages of temperature readings.  
The output is saved as:

- `curated/hourly_temperature.json`

This dataset is ready for dashboards, charts, or further analytical work.

---

## **Conclusion**

Through this project, I implemented all essential components of a modern data pipeline:

- ingestion of raw data  
- normalization into a unified schema  
- enrichment with metadata  
- quality control and validation  
- structured data lake zones  
- creation of a curated analytical dataset  

The result is a clean, maintainable, and fully traceable mini data lake aligned with industry best practices.
