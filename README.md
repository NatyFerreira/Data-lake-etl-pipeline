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
