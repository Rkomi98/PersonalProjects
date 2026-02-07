# EO Notebook: ingestion, access patterns, dataset engineering
![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?logo=numpy&logoColor=white)
![Pandas](https://img.shields.io/badge/pandas-150458?logo=pandas&logoColor=white)
![Xarray](https://img.shields.io/badge/xarray-EC5D57)
![Rasterio](https://img.shields.io/badge/rasterio-007C43)
![GeoPandas](https://img.shields.io/badge/GeoPandas-139C5A)
![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?logo=pytorch&logoColor=white)
![Zarr](https://img.shields.io/badge/Zarr-FFB000)

Questo progetto mostra una pipeline completa di **data engineering per Earth Observation** con Sentinel-2:

1. scoperta dati via STAC,
2. accesso efficiente a COG (cloud-optimized geotiff),
3. preprocessing per ML,
4. packaging del dataset in formato AI-ready,
5. quality checks,
6. esempio di data loader PyTorch.

L'obiettivo e dimostrare un workflow realistico e riusabile, non solo una demo “da notebook”.

## Cosa fa in pratica

Il notebook principale (`notebooks/eo_ingestion_access_dataset.ipynb`) esegue questi step:

- legge `config.yaml` (AOI, date, collezioni, bande, parametri preprocess),
- cerca scene Sentinel-2 su STAC (Planetary Computer),
- firma gli URL degli asset (SAS) per evitare errori HTTP 409/403,
- legge dati COG con pattern cloud-friendly (range/windowed access),
- costruisce uno stack coerente (`stackstac`) su griglia comune,
- applica cloud mask (`SCL`) e normalizzazione riflettanza,
- crea tile e split train/val,
- esporta:
  - cubo dati in `data/data.zarr`,
  - indice tile geospaziale in `data/tiles.parquet`,
  - statistiche per banda in `artifacts/statistics.json`,
  - metadati in `artifacts/metadata.json`,
  - report QC in `reports/qc_report.md` e `reports/qc_report.html`.

Inoltre `src/dataloader.py` fornisce un dataset/dataloader PyTorch con accesso lazy ai tile da Zarr.

## Struttura progetto

- `config.yaml`: configurazione pipeline (AOI, STAC, preprocess, output).
- `src/ingest_stac.py`: funzioni riusabili per discovery STAC e accesso COG.
- `src/dataloader.py`: `EOTileDataset` e `make_dataloader` per training.
- `notebooks/eo_ingestion_access_dataset.ipynb`: pipeline end-to-end spiegata passo passo.
- `pyproject.toml`: dipendenze per ambiente `uv`.
- `data/`, `artifacts/`, `reports/`: output generati dal notebook.

## Setup rapido con uv

Prerequisiti: `uv` installato.

```bash
uv venv
uv sync
uv run jupyter lab
```

Apri poi:

- `notebooks/eo_ingestion_access_dataset.ipynb`

ed esegui le celle dall’inizio alla fine.

## Configurazione

Modifica `config.yaml` per cambiare:

- AOI (`aoi.geometry`),
- finestra temporale (`stac.date_range`),
- cloud cover massimo (`stac.cloud_cover.max`),
- bande (`stac.assets`),
- tile size e preprocess (`preprocessing.*`).

## Note importanti

- `data/` e ignorata da git (`.gitignore`), quindi gli output pesanti non finiscono nel repository.
- Se il notebook resta aperto a lungo, gli URL firmati possono scadere: il codice fa refresh della firma prima dello stacking.
- Il salvataggio Zarr ripulisce automaticamente gli attributi non serializzabili (es. `RasterSpec`).

## Troubleshooting veloce

- `HTTP 409/403` su rasterio/stackstac:
  - causa tipica: URL non firmate o scadute;
  - soluzione: riesegui la cella discovery (firma item) e poi preprocessing.

- errori in cloud mask con `apply_ufunc`:
  - risolto nel notebook usando `scl.isin(...)` (shape-safe con xarray/dask).

- composito troppo piccolo / tile non sensati:
  - verifica AOI, date, EPSG e `preprocessing.target_resolution`;
  - se necessario usa AOI piu ampia o risoluzione meno fine.

## Perche esiste anche `src/`

Il notebook e utile per esplorazione e spiegazione.
I file in `src/` servono per riuso in script/pipeline batch (CI, orchestrazione, produzione).
