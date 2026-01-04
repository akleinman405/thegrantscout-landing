"""Centralized path management for Pipeline v2."""
import json
import logging
from pathlib import Path
from datetime import date

PIPELINE_ROOT = Path(__file__).parent.parent.parent
CONFIG_DIR = PIPELINE_ROOT / "config"
SQL_DIR = PIPELINE_ROOT / "sql"
TEMPLATES_DIR = PIPELINE_ROOT / "templates"
DATA_DIR = PIPELINE_ROOT / "data"
RUNS_DIR = PIPELINE_ROOT / "runs"
OUTPUTS_DIR = PIPELINE_ROOT / "outputs"
LOGS_DIR = PIPELINE_ROOT / "logs"


def load_client_registry() -> dict:
    """Load client registry from config/clients.json."""
    registry_file = CONFIG_DIR / "clients.json"
    if not registry_file.exists():
        return {"clients": []}
    with open(registry_file) as f:
        return json.load(f)


def setup_logging(client_name: str, script_name: str = None) -> logging.Logger:
    """Set up logging for a script run."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    # Create log filename
    log_date = date.today().isoformat()
    safe_name = client_name[:20].replace(" ", "_")
    log_file = LOGS_DIR / f"{log_date}_{safe_name}.log"

    # Configure logging
    logger = logging.getLogger(script_name or "pipeline")
    logger.setLevel(logging.DEBUG)

    # Remove existing handlers
    logger.handlers = []

    # File handler
    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(fh)

    # Console handler (INFO level)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(ch)

    return logger


def get_run_dir(client_name: str, run_date = None) -> Path:
    """Get or create run directory for a client.

    Args:
        client_name: Client name
        run_date: Date object or ISO date string (YYYY-MM-DD)
    """
    if run_date is None:
        run_date = date.today().isoformat()
    elif isinstance(run_date, date):
        run_date = run_date.isoformat()
    # run_date is now a string
    safe_name = client_name.replace(" ", "_")
    run_dir = RUNS_DIR / safe_name / run_date
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def get_output_dir(month: str = None) -> Path:
    """Get or create output directory for a month."""
    if month is None:
        month = date.today().strftime("%Y-%m")
    output_dir = OUTPUTS_DIR / month
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def get_latest_run_dir(client_name: str) -> Path:
    """Get most recent run directory for a client."""
    safe_name = client_name.replace(" ", "_")
    client_dir = RUNS_DIR / safe_name
    if not client_dir.exists():
        return None
    runs = sorted(client_dir.iterdir(), reverse=True)
    return runs[0] if runs else None
