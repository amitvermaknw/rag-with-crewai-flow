#!/usr/bin/env python
from pydantic import BaseModel
from crewai.flow import Flow, listen, start, router
from rag_with_crewai_flow.crews.websearch_crew.websearch_crew import WebsearchCrew
from rag_with_crewai_flow.crews.services.bigquery_service import BigQueryService
from rag_with_crewai_flow.crews.core.generate_embedding import GenerateEmbedding
from rag_with_crewai_flow.crews.summary_crew.summary_crew import SummaryCrew
from rag_with_crewai_flow.crews.services.firebase_service import FirebaseService
from rag_with_crewai_flow.schemas.articles import ArticleSearchOutput


#Define flow state
class ArticleState(BaseModel):
    query: str =""
    cache_hit: bool = False
    raw_article: ArticleSearchOutput = ""
    summary: str = ""
    embedding: list = []
    articles: list = []

class ArticleRagFlow(Flow[ArticleState]):
    def __init__(self):
        super().__init__()
        self.bg_service = BigQueryService()
        self.fb_service = FirebaseService()

    @start()
    def check_vecor_db(self):
        """
        Hit to cached/vector DB for articles.
        """
        print("Check article in vector db")
        self.bg_service.check_bigquery_cache(self.state)
        
    @router(check_vecor_db)
    def route_after_cahec(self):
        """
        Check if vector db found article or not
        """
        if self.state.cache_hit:
            return self.state.articles
        return "not_found"

    @listen("not_found")
    def fetch_from_web(self):
        """
        Fetch searched article from web using task and agent.
        Summarized the article
        """
        print("Fetch query from web")
        result = WebsearchCrew().crew().kickoff(
            inputs={"query": self.state.query}
        )  
        self.state.raw_article = result

    @listen(fetch_from_web)
    def generate_embedding(self):
        self.state.embedding = GenerateEmbedding(self.state.raw_article)

    @listen(generate_embedding)
    def save_data(self):
        self.fb_service.save_article(self.state.raw_article["articles"][0])
        self.bg_service.save_article(self.state.raw_article["articles"][0])

    @listen("cache_hit")
    @listen(save_data)
    def return_result(self):
        return self.state.articles
    

    
# @listen(fetch_from_web)
    # def summarize_article(self):
    #     """
    #     Summaries the article
    #     """
    #     print("Summarize the articles")
    #     result = SummaryCrew().crew().kickoff(
    #         inputs = {"content": self.state.raw_article}
    #     )
    #     self.state.summary = result

# def kickoff():
#     poem_flow = WebsearchCrew()
#     poem_flow.kickoff()


# def plot():
#     poem_flow = WebsearchCrew()
#     poem_flow.plot()


# def run_with_trigger():
#     """
#     Run the flow with trigger payload.
#     """
#     import json
#     import sys

#     # Get trigger payload from command line argument
#     if len(sys.argv) < 2:
#         raise Exception("No trigger payload provided. Please provide JSON payload as argument.")

#     try:
#         trigger_payload = json.loads(sys.argv[1])
#     except json.JSONDecodeError:
#         raise Exception("Invalid JSON payload provided as argument")

#     # Create flow and kickoff with trigger payload
#     # The @start() methods will automatically receive crewai_trigger_payload parameter
#     poem_flow = WebsearchCrew()

#     try:
#         result = poem_flow.kickoff({"crewai_trigger_payload": trigger_payload})
#         return result
#     except Exception as e:
#         raise Exception(f"An error occurred while running the flow with trigger: {e}")


# if __name__ == "__main__":
#     kickoff()
