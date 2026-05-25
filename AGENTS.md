# AI Agent Guide for TE_dashboard_backend

## Overview
This repository is a Python backend for TE Dashboard data extraction, transformation, and reporting.
It consists primarily of standalone scripts and cron-run batch jobs rather than a packaged Python application.

## Key characteristics
- Root-level Python scripts are the main entrypoints.
- The project uses a committed `venv/` directory; do not modify or rely on packages inside it when changing code.
- The environment is configured with `requirements.txt` and `create_env.sh`.
- `settings.py` contains the database and logging configuration used by most scripts.
- There is no package metadata (`setup.py`, `pyproject.toml`) or dedicated tests in the repository.

## Setup
- Use Python 3 and a virtual environment.
- Install dependencies with:
  - `python3 -m venv venv`
  - `source venv/bin/activate`
  - `pip install --upgrade pip`
  - `pip install -r requirements.txt`
- `create_env.sh` is the repository setup helper and also defines cron jobs for scheduled tasks.

## Runtime expectations
- The project expects MySQL credentials and database details from `settings.py`.
- It also writes logs and CSV output under `/var/log/czentrix/TE_dashboard/`.
- `compute_layer_functions_api.py` exposes FastAPI routes.
- Other important scripts include:
  - `data_layer.py`
  - `compute_layer.py`
  - `create_filter.py`
  - `live_data.py`
  - `acquire_lock.py`
  - `delete_365days_old_data.py`
  - `service_check.py`
  - `yearly_*` scripts for annual operations

## Guidance for code changes
- Preserve existing script-based patterns and `if __name__ == "__main__"` entrypoints.
- Keep changes focused on the repo’s procedural, batch-oriented style.
- Avoid refactoring into a package layout or adding packaging scaffolding unless explicitly requested.
- Do not edit, generate, or depend on code inside `venv/` or `__pycache__/`.
- Keep database credentials and operational configuration in `settings.py` unless the task explicitly calls for externalizing configuration.

## What to avoid
- Don’t add a new `setup.py` or `pyproject.toml` unless the user asks for packaging support.
- Don’t create tests in a new format unless you confirm the repo wants that direction.
- Don’t assume an existing CI/test harness; there is no clear test configuration in the workspace.

## Useful files
- `create_env.sh` — environment setup and cron registration.
- `requirements.txt` — pinned dependencies, including FastAPI and pandas.
- `settings.py` — database host/user/password, API server host/port, log and CSV file paths.
- `compute_layer_functions_api.py` — FastAPI application exposing data endpoints.

## Notes for future agent customization
- A separate skill or prompt can be added later for common maintenance tasks like: "Update cron jobs", "Refactor data pipeline scripts", or "Document entrypoint scripts."