from pydantic import BaseModel
from typing import List

class Article(BaseModel):
    title: str
    article_url: str
    content: str
    summary: str
    image_url: str
    publishedat: str

class ArticleSearchOutput(BaseModel):
    articles: List[Article]
    total_found: int
    