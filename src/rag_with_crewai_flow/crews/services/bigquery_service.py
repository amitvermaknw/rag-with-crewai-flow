from google.cloud import bigquery
from google.oauth2 import service_account
from rag_with_crewai_flow.crews.core.config import settings 
from rag_with_crewai_flow.crews.core.generate_embedding import GenerateEmbedding

class BigQueryService:
    def __init__(self):
        creds = service_account.Credentials.from_service_account_file(
            settings.bigquery_cred_path
        )
        self.client = bigquery.Client(project=settings.bigquery_project_id, credentials=creds)
        self.table_id = f"{settings.bigquery_project_id}.{settings.bigquery_dataset}.{settings.bigquery_table}"
        

    def check_bigquery_cache(self):
        "Check first BigQuery vector db"

        query_embedding = GenerateEmbedding(self.state.query)
        embedding_str = ", ".join(map(str, query_embedding))

        query = f"""
            SELECT base.articleId, base.title, base.summary FROM VECTOR_SEARCH(
                TABLE `{settings.bigquery_project_id}.{settings.bigquery_dataset}.{settings.bigquery_table}`,
                'embedding',
                (SELECT [{embedding_str}] AS embedding),
                top_k=5,
                distance_type => 'COSINE'
            )
            WHERE distance < 0.15 -- similarity threshold, tune this ORDER by distance ASC
        """
        try:
            query_job = self.client.query(query)
            results = query_job.result()
            rows = list(results)

            if rows:
                self.state.cache_hit = True
                self.state.articles = [
                    {
                        "article_id": row.articlesId,
                        "title": row.title,
                        "summary": row.summary,
                        "similarity_score": 1 - row.distance 
                    }
                    for row in rows
                ]
            else:
                self.state.cache_hit = False
                self.state.articles = []

        except Exception as e:
            print(f"BigQuery cache check failed: {e}")
            self.state.cache_hit = False
            self.state.articles = []