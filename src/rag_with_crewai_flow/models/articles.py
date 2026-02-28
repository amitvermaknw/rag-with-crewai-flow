from crewai.flow.flow import Flowstate
from pydantic import BaseModel
from typing import Optional

class RAGFlowState(Flowstate):
    query: str = ""
    cache_hit: bool = False
    articles: list[dict] = []
    final_answer: str = ""
    