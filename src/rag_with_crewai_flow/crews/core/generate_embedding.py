from vertexai.language_models import TextEmbeddingModel
import vertexai
from rag_with_crewai_flow.crews.core.config import settings 
from google.oauth2 import service_account

class GenerateEmbedding():
    def __init__(self, text):
        creds = service_account.Credentials.from_service_account_file(
            settings.bigquery_cred_path,
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        vertexai.init(
            project=settings.bigquery_project_id,
            location=settings.location,
            credentials=creds 
        )
        model = TextEmbeddingModel.from_pretrained("text-embedding-004")
        embeddings = model.get_embeddings([text])
        return embeddings[0].values