from fastapi import APIRouter
from pydantic import BaseModel
from rag_with_crewai_flow.article_rag_flow import ArticleRagFlow

app = APIRouter(
    prefix="/api/v1",
    tags=["articles"]
)

class SearchRequest(BaseModel):
    query: str

@app.post("/search")
async def search(request: SearchRequest):
    flow = ArticleRagFlow()
    result = await flow.kickoff_async(inputs={
        "query": request.query
    })
    
    return {"code": 200, "status": "success", "msg": result}