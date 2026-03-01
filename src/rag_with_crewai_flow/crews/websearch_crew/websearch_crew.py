from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from pydantic import BaseModel
from rag_with_crewai_flow.schemas.articles import Article

class ArticleSearchOutput(BaseModel):
    articles: List[Article]
    total_found: int

@CrewBase
class WebsearchCrew():
    """WebsearchCrew crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    @agent
    def web_searcher(self) -> Agent:
        return Agent(
            config=self.agents_config['web_searcher'],
            verbose=True
        )

    @agent
    def content_extractor(self) -> Agent:
        return Agent(
            config=self.agents_config['content_extractor'],
            verbose=True
        )

    @task
    def search_articles_task(self) -> Task:
        return Task(
            config=self.tasks_config['search_articles_task'], 
        )

    @task
    def extract_content_task(self) -> Task:
        return Task(
            config=self.tasks_config['extract_content_task'], # type: ignore[index]
            output_pydantic=ArticleSearchOutput
        )

    @crew
    def crew(self) -> Crew:
        """Creates the WebsearchCrew crew"""
        return Crew(
            agents=self.agents, 
            tasks=self.tasks, 
            process=Process.sequential,
            verbose=True,
        )
