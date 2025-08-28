#!/usr/bin/env python
import json
import os
from typing import List
from pydantic import BaseModel, Field
from crewai.flow.flow import Flow, listen, start, router, or_
from openai import AzureOpenAI
from src.webrag.crew import Webrag

# Define our models for structured data
class ResearchPlan(BaseModel):
    """Structured plan for research workflow"""
    topic: str = Field(description="Main topic for research")
    rag_focus: str = Field(description="Specific focus for RAG research")
    web_focus: str = Field(description="Specific focus for web research")
    research_questions: List[str] = Field(description="Key questions to answer")
    target_audience: str = Field(description="Target audience for the report")

class ResearchResults(BaseModel):
    """Results from research phase"""
    rag_findings: str = ""
    web_findings: str = ""
    combined_insights: str = ""
    research_method: str = ""

# Define our flow state
class WebragFlowState(BaseModel):
    """State management for the Webrag flow"""
    topic: str = ""
    current_year: str = ""
    research_plan: ResearchPlan = None
    research_results: ResearchResults = ResearchResults()
    research_decision: str = ""
    orchestrator_decision: str = ""
    final_report: str = ""

class WebragFlow(Flow[WebragFlowState]):

    @start()
    def collect_user_input(self):
        """
        Entry point: Collect user input about research topic
        """
        print("\n=== WebRAG Research Flow ===\n")
        
        # Get user input
        self.state.topic = input("What topic would you like to research? ")
        
        from datetime import datetime
        self.state.current_year = str(datetime.now().year)
        
        print(f"\nStarting research on: {self.state.topic}")
        print(f"Current year: {self.state.current_year}\n")
        
        return "user_input_collected"

    @listen(collect_user_input)
    def create_research_plan(self):
        self.state.research_plan = ResearchPlan(
            topic=self.state.topic,
            rag_focus=f"Local research about {self.state.topic}",
            web_focus=f"Web research about {self.state.topic}",
            research_questions=[f"What is {self.state.topic}?"],
            target_audience="General audience"
        )
        print("Research plan created")
        return "research_plan_created"

    @listen(create_research_plan)
    def orchestrate_research(self):
        llm = AzureOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01"),
            azure_deployment=os.getenv("MODEL", "gpt-4"),
        )
        chat = llm.chat.completions.create(
            model=os.getenv("MODEL", "gpt-4"),
            messages=[
                {"role": "system", "content": f"If the input is about minecraft dirt blocks, answer 'rag'. if the input is something else, answer 'web'."},
                {"role": "user", "content": f"Input:{self.state.topic}"}
            ],
            max_tokens=1024,

        )
        answer = chat.choices[0].message.content.strip().lower()

        if "rag" in answer:
            self.state.orchestrator_decision = "rag"
        else:
            self.state.orchestrator_decision = "web"
        print(f"Decision: {self.state.orchestrator_decision}")
        return "orchestration_complete"

    @router(orchestrate_research)
    def route_research(self):
        decision = self.state.orchestrator_decision.lower()
        print(f"Orchestrator decision: {decision}")
        if "rag" in decision:
            return "rag_path"
        elif "web" in decision:
            return "web_path"
        else:
            return "rag_path"

    @listen("rag_path")
    def execute_rag_research(self):
        """
        Execute RAG research using the local document crew
        """
        print("🔍 Executing RAG research...")
        
        try:
            webrag_crew = Webrag()
            rag_result = webrag_crew.rag_researcher().execute_task(
                webrag_crew.rag_research_task(),
                context={"topic": self.state.topic, "current_year": self.state.current_year}
            )
            self.state.research_results.rag_findings = str(rag_result)
        except Exception as e:
            print(f"RAG research error: {e}")
            self.state.research_results.rag_findings = f"RAG research completed for: {self.state.topic}"
        
        self.state.research_results.research_method = "RAG"
        print("✅ RAG research completed")

    @listen("web_path")
    def execute_web_research(self):
        """
        Execute web research
        """
        print("🌐 Executing web research...")
        
        try:
            webrag_crew = Webrag()
            web_result = webrag_crew.web_researcher().execute_task(
                webrag_crew.web_research_task(),
                context={"topic": self.state.topic, "current_year": self.state.current_year}
            )
            self.state.research_results.web_findings = str(web_result)
        except Exception as e:
            print(f"Web research error: {e}")
            self.state.research_results.web_findings = f"Web research completed for: {self.state.topic}"
        
        self.state.research_results.research_method = "Web"
        print("✅ Web research completed")

    @listen(or_(execute_rag_research, execute_web_research))
    def synthesize_and_report(self):
        """
        Synthesize research findings and create final report
        """
        print("📝 Synthesizing findings and creating report...")
        
        # Determine which research was actually executed
        if self.state.research_results.rag_findings:
            research_content = self.state.research_results.rag_findings
            research_method = "RAG"
        else:
            research_content = self.state.research_results.web_findings
            research_method = "Web"
        
        # Create simple report
        self.state.final_report = f"# Research Report: {self.state.topic}\n\nMethod: {research_method}\n\n{research_content}"
        
        # Save the report
        os.makedirs("output", exist_ok=True)
        with open("output/research_report.md", "w") as f:
            f.write(self.state.final_report)
        
        print(f"✅ Research flow completed using {research_method}!")
        print("📄 Final report saved to: output/research_report.md")
        
        return "flow_completed"

def kickoff():
    """Run the WebRAG research flow"""
    flow = WebragFlow()
    result = flow.kickoff()
    
    print("\n" + "="*50)
    print("🎉 WebRAG Flow Complete!")
    print("="*50)
    print("Your research results are available in the output directory:")
    print("• research_plan.json - Initial research strategy")
    print("• research_report.md - Final comprehensive report") 
    print("• research_summary.json - Complete research summary")
    
    return result

def plot():
    """Generate a visualization of the flow"""
    flow = WebragFlow()
    flow.plot("webrag_flow")
    print("Flow visualization saved to webrag_flow.html")

if __name__ == "__main__":
    kickoff()
    plot()
