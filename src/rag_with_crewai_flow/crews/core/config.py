from pydantic_settings import BaseSetting
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

class Setting(BaseSetting):
    bigquery_cred_path: str
    bigquery_project_id: str
    bigquery_dataset: str
    bigquery_table: str
    location: str

    model_config = {
        "env_file": str(ROOT_DIR/".env"),
        "env_file_encoding": "utf-8"
    }

settings = Setting()
    