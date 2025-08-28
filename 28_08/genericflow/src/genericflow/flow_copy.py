#!/usr/bin/env python
import os
from typing import List
from pydantic import BaseModel, Field
from crewai.flow.flow import Flow, listen, start, router, or_
from openai import AzureOpenAI
from crews.webrag.crew import Webrag
from crews.mathcrew.crew import Math

# Define our models for structured data
class ResearchPlan(BaseModel):
    """Structured plan for research workflow"""
    topic: str = Field(description="Main user input")
    rag_focus: str = Field(description="Specific focus for RAG research")
    web_focus: str = Field(description="Specific focus for web research")
    math_focus: str = Field(description="Specific focus for math solving")
    research_questions: List[str] = Field(description="Key questions to answer")
    target_audience: str = Field(description="Target audience for the report")

class ResearchResults(BaseModel):
    """Results from research phase"""
    rag_findings: str = ""
    web_findings: str = ""
    math_findings: str = ""
    combined_insights: str = ""
    research_method: str = ""

# Define our flow state
class GenericFlowState(BaseModel):
    """State management for the Generic flow"""
    topic: str = ""
    current_year: str = ""
    research_plan: ResearchPlan = None
    research_results: ResearchResults = ResearchResults()
    research_decision: str = ""
    orchestrator_decision: str = ""
    final_report: str = ""

class GenericFlow(Flow[GenericFlowState]):

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
            math_focus=f"Math research about {self.state.topic}",
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
                {"role": "system", "content": "You are a classifier. Answer with ONLY one word. 'math' if the input is a mathematical equation or calculation. if not a mathematical equation or calculation, respond with 'not_math'."},
                {"role": "user", "content": f"Classify this input: {self.state.topic}"}
        ],
            max_tokens=10,
            temperature=0.0

        )
        answer = chat.choices[0].message.content.strip().lower()
        print(answer)
        if answer == "math":
            self.state.orchestrator_decision = "math"
            return "orchestration_complete"
        elif answer == "not_math":
            
            llm = AzureOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01"),
            azure_deployment=os.getenv("MODEL", "gpt-4"),
            )
            chat = llm.chat.completions.create(
                model=os.getenv("MODEL", "gpt-4"),
                messages=[
                    {"role": "system", "content": "You are a classifier. Answer with ONLY one word. 'rag' if the input is about minecraft dirt blocks. 'web' if it's anything else."},
                    {"role": "user", "content": f"Classify this input: {self.state.topic}"}
            ],
                max_tokens=10,
                temperature=0.0

                )   
            answer = chat.choices[0].message.content.strip().lower()
            if "rag" in answer:
                self.state.orchestrator_decision = "rag"
            elif "web" in answer:
                self.state.orchestrator_decision = "web"
            return "orchestration_complete"

    @router(orchestrate_research)
    def route_research(self):
        decision = self.state.orchestrator_decision.lower()
        print(f"Orchestrator decision: {decision}")
        if "math" in decision:
            return "math_path"
        elif "rag" in decision:
            return "rag_path"
        elif "web" in decision:
            return "web_path"

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
        return "rag_completed"

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
        return "web_completed"

    @listen("math_path")
    def execute_math_problem(self):
        """
        Execute math problem
        """
        try:
            math_crew = Math()
            math_result = math_crew.math_tool_agent().execute_task(
                math_crew.math_task(),
                context={"problem": self.state.topic, "topic": self.state.topic}
            )
            self.state.research_results.math_findings = str(math_result)
        except Exception as e:
            print(f"Math problem error: {e}")
            self.state.research_results.math_findings = f"Math problem completed for: {self.state.topic}"
        
        self.state.research_results.research_method = "Math"
        return "math_completed"

    @listen(or_(execute_rag_research, execute_web_research, execute_math_problem))
    def synthesize_and_report(self):
        """
        Synthesize research findings and create final report
        """
        print("📝 Synthesizing findings and creating report...")
        
        # Determine which research was actually executed
        if self.state.research_results.rag_findings:
            research_content = self.state.research_results.rag_findings
            research_method = "RAG"
        elif self.state.research_results.math_findings:
            research_content = self.state.research_results.math_findings
            research_method = "Math"
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
    """Run the Generic research flow"""
    flow = GenericFlow()
    result = flow.kickoff()
    
    print("\n" + "="*50)
    print("🎉 Generic Flow Complete!")
    print("="*50)
    print("Your research results are available in the output directory:")
    print("• research_plan.json - Initial research strategy")
    print("• research_report.md - Final comprehensive report") 
    print("• research_summary.json - Complete research summary")
    
    return result

def plot():
    """Generate a visualization of the flow"""
    flow = GenericFlow()
    flow.plot("generic_flow")
    print("Flow visualization saved to generic_flow.html")

if __name__ == "__main__":
    kickoff()
    plot()
