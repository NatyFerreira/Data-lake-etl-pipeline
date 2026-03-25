# ESTRUTURAÇÃO DO DATA LAKE

import csv # para ler/gravar arquivos CSV
import json # para ler/gravar arquivos JSON
from collections import defaultdict # facilita agrupar valores por chave (no caso, por hora)
from datetime import datetime, timezone, timedelta # para trabalhar com datas e timezone correto (Europa/Paris)
from pathlib import Path # caminho de arquivos de forma elegante

PARIS_TZ = timezone(timedelta(hours=1))

# 3 zonas do data lake (raw, processed, curated)
RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
CURATED_DIR = Path("data/curated") 

# LEITURA DAS FONTES DE DADOS 

def load_business_csv(path: Path): # lê o business.csv e devolve uma lista de dicionários (cada linha = um dict)
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))

def load_sensor_json(path: Path): # lê o sensor.json e devolve a lista de eventos de sensores
    with path.open(encoding="utf-8") as f:
        return json.load(f)
# Esse código acima é EXTRACT PURO (abre o arquivo .csv ou .json, transforma cada linha em um dicionário Python e devolve a lista de registros brutos)

# NORMALIZAÇÃO DOS DADOS (TRANSFORM)
# pega cada linha dos arquivos e transforma em um formato padronizado
def normalize_business(rows):
    normalized = []
    for row in rows:
        normalized.append({
            "source": "business",
            "event_time": row["event_time"],
            "entity_id": row["customer_id"],
            "site": row["site"],
            "metric": row["metric_type"],
            "value": float(row["value"]), # converte value para float, garante tipo numérico consistente
            "unit": row["unit"],
        })
    return normalized
# a nomralização acontece aqui da mesma forma, mas adaptando os nomes dos campos
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
            "status": row.get("status", "unknown"), # aqui assume "unknown" se não tiver status
        })
    return normalized
# Essa parte aqui do código transforma em "formato comum"

# FUNÇÃO GENÉRICA PARA SALVAR EM JSON
def save_json(data, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True) # garante que a pasta existe (cria automaticamente a pasta onde o arquivo deve ser salvo) / não importa se é data/processed ou curated
    with path.open("w", encoding="utf-8") as f: # abre o arquivo no caminho exato 
        json.dump(data, f, indent=2) # salva o conteúdo em JSON bonito (ident=2) 

def build_metadata(business_rows, sensor_rows, normalized_count):
    return {
        # Data e hora do processamento (traçabilidade)
        "generated_at": datetime.now(PARIS_TZ).isoformat(), # traçabilidade (data/hora do processamento)
        
        # Fontes utilizadas (nome, formato e número de registros)
        "sources": [ 
            {"name": "business.csv", "format": "csv", "records": len(business_rows)},
            {"name": "sensor.json", "format": "json", "records": len(sensor_rows)},
        ],

        # Número total de linhas após normalização
        "total_normalized_records": normalized_count,

        # Zonas do data lake (documentação)
        "zones": ["raw", "processed", "curated"], 
    }

def aggregate_hourly_temperature(rows): 
    buckets = defaultdict(list)
    for row in rows:
        if row["metric"] != "temperature_c": # filtra só eventos com "metric == temperature_c"
            continue
        dt = datetime.fromisoformat(row["event_time"])
        hour_key = dt.replace(minute=0, second=0, microsecond=0).isoformat() # agrupa por hora (zera minuto/segundo/microsegundo)
        buckets[hour_key].append(row["value"]) # calcula média por hora e número de amostras

    output = []
    for hour_key, values in sorted(buckets.items()):
        output.append({
            "hour": hour_key,
            "avg_temperature_c": round(sum(values) / len(values), 2),
            "samples": len(values),
        })
    return output

def build_quality_report(sensor_rows):
    warnings = [row for row in sensor_rows if row.get("status") == "warning"] # conta quantos eventos têm "status = warning"
    high_temp = [row for row in sensor_rows if float(row["temperature_c"]) > 28] # conta quantos têm temperatura alta (> 28) 
    low_temp = [row for row in sensor_rows if float(row["temperature_c"]) < 15] # conta quantos têm temperatura baixa (< 15)
    
    # Detecta linhas sem o campo "status"
    missing_status = [row for row in sensor_rows if "status" not in row]

    return {
        "warning_count": len(warnings),
        "high_temperature_count": len(high_temp),
        "low_temperature_count": len(low_temp),
        "missing_status_count": len(missing_status),
        
        "examples": {
            "warning": warnings[:3], # guarda alguns exemplos (até 3) de cada tipo
            "high_temperature": high_temp[:3],
            "low_temperature": low_temp[:3],
            "missing_status": missing_status[:3],
        },
    }

# FUNÇÃO PRINCIPAL: O PIPELINE COMPLETO
# Aqui é o onde o EXTRACT é chamado no pipeline, onde ele realmente EXECUTA o extract e prepara para a etapa de transformação
def main():
    business_rows = load_business_csv(RAW_DIR / "business.csv")
    sensor_rows = load_sensor_json(RAW_DIR / "sensor.json")

    normalized = normalize_business(business_rows) + normalize_sensor(sensor_rows)
    save_json(normalized, PROCESSED_DIR / "normalized_events.json")
    save_json(
        build_metadata(business_rows, sensor_rows, len(normalized)), 
              PROCESSED_DIR / "metadata.json"
    )
# Nota:
# Arquivos em data/curated/ representam dados prontos para análise.
# Aqui salvamos agregações, métricas derivadas e datasets finais.
# O arquivo hourly_temperature.json é um produto analítico (média por hora),
# portanto pertence à zona curated.

    save_json(aggregate_hourly_temperature(normalized), CURATED_DIR / "hourly_temperature.json")
    save_json(build_quality_report(sensor_rows), PROCESSED_DIR / "quality_report.json") 

# Nota:
# O quality_report deve ser salvo apenas em data/processed/.
# A zona processed é responsável por armazenar dados limpos, normalizados
# e todos os relatórios de qualidade e auditoria.
# A zona curated deve conter somente dados prontos para análise (ex: agregações).
# Por isso NÃO duplicamos o quality_report em curated.


    print(f"Processed {len(normalized)} normalized events")

if __name__ == "__main__":
    main()
