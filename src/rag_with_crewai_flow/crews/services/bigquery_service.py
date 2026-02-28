from google.cloud import bigquery
from google.oauth2 import service_account
from rag_with_crewai_flow.crews.core.config import settings 

class BigQueryService:
    def __init__(self):
        creds = service_account.Credentials.from_service_account_file(
            settings.bigquery_cred_path
        )
        self.client = bigquery.Client(project=settings.bigquery_project_id, credentials=creds)
        table_id = f"{settings.bigquery_project_id}.{settings.bigquery_dataset}.{settings.bigquery_table}"
    