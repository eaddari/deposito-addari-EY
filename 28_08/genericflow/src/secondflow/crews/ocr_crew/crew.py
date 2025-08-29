from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from crewai_tools import SerperDevTool
from tools.custom_tool import LocalRag
import os
import ssl

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

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
class ExplanationCrew():
    """Explanation crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    @agent
    def agent_manager(self) -> Agent:
        """
        Manages the agent's tasks and responsibilities by deciding how to write the explanation of the topic.
        """
        return Agent(
            config=self.agents_config['agent_manager'],
            verbose=True,
            llm=crew_llm
        )
    @agent
    def web_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['web_researcher'],
            verbose=True,
            tools=[web_search_tool],
            llm=crew_llm
        )
    @agent
    def expert_writer(self) -> Agent:
        return Agent(
            config=self.agents_config['expert_writer'],
            verbose=True,
            llm=crew_llm
        )

    @task
    def agent_manager_task(self) -> Task:
        return Task(
            config=self.tasks_config['agent_manager_task']
        )
    @task
    def web_researcher_task(self) -> Task:
        return Task(
            config=self.tasks_config['web_research_task']
        )
    @task
    def expert_writer_task(self) -> Task:
        return Task(
            config=self.tasks_config['expert_writer_task']
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Explanation crew"""

        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
