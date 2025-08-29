from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import sys
import os
from dotenv import load_dotenv
from pathlib import Path
from openai import AzureOpenAI
load_dotenv()

class MyCustomToolInput(BaseModel):
    """Input schema for MyCustomTool."""
    question: str = Field(..., description="Question to ask the tool.")

class LocalRag(BaseTool):
    name: str = "Local RAG"
    description: str = (
        "This tool performs local retrieval-augmented generation using FAISS and Azure OpenAI. "
        "It can answer questions based on local documents using a RAG pipeline with embeddings, "
        "vector search, and response generation. Provide a question and get an answer with source citations."
    )
    args_schema: Type[BaseModel] = MyCustomToolInput
    
    def _get_python_executable(self):
        """Get the Python executable path for the virtual environment."""
        webrag_root = Path(__file__).parent.parent.parent.parent
        venv_python = webrag_root / ".venv" / "Scripts" / "python.exe"
        if venv_python.exists():
            return str(venv_python)
        return "python"  # fallback
    
    def _load_rag_functions(self):
        """Import RAG functions dynamically."""
        try:
            # Add the rag directory to Python path
            rag_dir = Path(__file__).parent.parent.parent / "rag"
            if str(rag_dir) not in sys.path:
                sys.path.insert(0, str(rag_dir))
            
            # Import the functions we need
            import faiss_rag
            
            return faiss_rag
            
        except ImportError as e:
            raise RuntimeError(f"Could not import faiss_rag module: {str(e)}")

    def _run(self, question: str) -> str:
        """Run the RAG system with the provided question."""
        try:
            # Load RAG functions
            faiss_rag = self._load_rag_functions()
            
            # Initialize components
            settings = faiss_rag.SETTINGS
            embeddings = faiss_rag.get_embeddings(settings)
            llm_model = faiss_rag.llm()
            
            # Load or build vector store
            docs = faiss_rag.corpus()
            vector_store = faiss_rag.load_or_build_vectorstore(settings, embeddings, docs)
            
            # Create retriever and chain
            retriever = faiss_rag.make_retriever(vector_store, settings)
            rag_chain = faiss_rag.build_rag_chain(llm_model, retriever)
            
            # Get answer
            answer = faiss_rag.rag_answer(question, rag_chain)
            
            return answer
            
        except Exception as e:
            return f"Error running RAG query: {str(e)}\n\nPlease ensure your Azure OpenAI credentials are properly configured in the .env file."

class MathEquationsTool(BaseTool):
    name: str = "Math Equations Solver"
    description: str = (
        "This tool solves mathematical equations and provides step-by-step solutions. "
        "Input a math problem, and it will return the solution along with the steps taken to solve it."
    )
    args_schema: Type[BaseModel] = MyCustomToolInput
    
    def _run(self, question: str) -> str:
        """Run the math equations solver with the provided question."""
        try:
            client = AzureOpenAI(
                deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
                model=os.getenv("AZURE_OPENAI_MODEL"),
                temperature=0,
                max_retries=3
            )
    
            response = client.chat.completions.create(
                model=os.getenv("AZURE_OPENAI_MODEL"),
                messages=[
                    {"role": "system", "content": "You are a helpful math assistant which transforms user input into correct math equations. The equations must be runnable in standard python."},
                    {"role": "user", "content": question}
                ]
            )

            return response.choices[0].message.content

        except Exception as e:
            return f"Error executing math solver: {str(e)}"