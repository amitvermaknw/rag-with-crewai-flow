import firebase_admin
from firebase_admin import credentials, firestore
from rag_with_crewai_flow.crews.core.config import settings 
from rag_with_crewai_flow.crews.core.generate_embedding import GenerateEmbedding

class FirebaseService:
    def __init__(self):
        if not firebase_admin._apps:
            cred = credentials.Certificate(settings.firebase_cred_path)
            firebase_admin.initialize_app(cred)
        
        self.firestore_client = firestore.client()