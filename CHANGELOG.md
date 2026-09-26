# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-09-26

### Added

- FastAPI inference service (`api/main.py`, `api/inference.py`) with `/health` and `/predict` endpoints
- Docker + Docker Compose setup for CPU-only inference
- Desktop UI (`main.py`) connected to the API with configurable `DETECTION_API_URL`
- Automated tests for API (`tests/test_api.py`) and ACDC conversion (`tests/test_acdc_conversion.py`)
- GitHub Actions CI: pytest + Docker build
- Split requirements files: `requirements-api.txt`, `requirements-ui.txt`, `requirements-test.txt`
- Project documentation (`README.md`, `CONTRIBUTING.md`, `CHANGELOG.md`)

### Model

- Baseline YOLOv8n trained on ACDC (all 4 weather conditions, 8 classes)
- mAP@0.5 = 0.2664, mAP@0.5:0.95 = 0.1538
- Trained weights are kept local and mounted via Docker volume
