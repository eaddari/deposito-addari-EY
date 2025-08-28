from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from crewai_tools import SerperDevTool
from .tools.custom_tool import LocalRag
from langchain_openai import AzureChatOpenAI
import os
import ssl
import httpx

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

azure_llm = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01"),
    azure_deployment=os.getenv("MODEL", "gpt-4"),
    temperature=0.1,
    http_client=httpx.Client(verify=False)
)

from crewai.llm import LLM

crew_llm = LLM(
    model=f"azure/{os.getenv('MODEL', 'gpt-4')}",
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    base_url=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01"),
    temperature=0.1)

web_search_tool = SerperDevTool()

local_rag_tool = LocalRag()

@CrewBase
class Webrag():
    """Webrag crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    @agent
    def rag_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['rag_researcher'],
            verbose=True,
            tools=[local_rag_tool],
            llm=crew_llm
        )
    @agent
    def web_researcher(self) -> Agent:
        # Use available tools, fallback if web tools fail
        tools = [web_search_tool] if web_search_tool else []
        return Agent(
            config=self.agents_config['web_researcher'],
            verbose=True,
            tools=tools,
            llm=crew_llm
        )
    @agent
    def reporting_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['reporting_analyst'],
            verbose=True,
            llm=crew_llm
        )

    @task
    def web_research_task(self) -> Task:
        return Task(
            config=self.tasks_config['web_research_task'],
        )
    @task
    def rag_research_task(self) -> Task:
        return Task(
            config=self.tasks_config['rag_research_task'],
        )
    @task
    def reporting_task(self) -> Task:
        return Task(
            config=self.tasks_config['reporting_task'],
            output_file='report.md'
        )


    @crew
    def crew(self) -> Crew:
        """Creates the Webrag crew"""

        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
