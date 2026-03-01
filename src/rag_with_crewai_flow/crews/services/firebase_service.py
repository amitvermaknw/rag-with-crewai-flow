import firebase_admin
from firebase_admin import credentials, firestore
from rag_with_crewai_flow.crews.core.config import settings 
from rag_with_crewai_flow.crews.core.generate_embedding import GenerateEmbedding
from rag_with_crewai_flow.util.util import Util
from datetime import datetime

class FirebaseService:
    def __init__(self):
        if not firebase_admin._apps:
            cred = credentials.Certificate(settings.firebase_cred_path)
            firebase_admin.initialize_app(cred)
        
        self.firestore_client = firestore.client()
        self.collection = "inbits_collection/us/articles"

    def save_article(self, data: dict) -> str:
        doc_ref = self.firestore_client.collection(self.collection).document()
        payload = {
            "country": "us",
            "articleId": Util().slug_id(),
            "slug": Util.generate_slug(data.get("title"), Util().slug_id()),
            "description": data.get("content"),
            "summary": {
                "category": "politics",
                "title": data.get("title"),
                "summary": data.get("summary")
            },
            "author": "Tom Nicholson",
            "url": data.get("article_url"),
            "urlToImage": data.get("image_url"),
            "content": None,
            "source": {
                "name": "POLITICO.eu",
                "id": None
            },
            "publishedAt": datetime.now(),
            "title": data.get("title")
        }   

        doc_ref.set(payload)
        print(f"Saved to Firestore: {doc_ref.id}")
        return doc_ref.id