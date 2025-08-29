from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import List

from langchain.schema import Document
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain.text_splitter import RecursiveCharacterTextSplitter

# LangChain Core (prompt/chain)
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from langchain.chat_models import init_chat_model
from dotenv import load_dotenv

from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI



# =========================
# Configurazione
# =========================

load_dotenv()

@dataclass
class Settings:
    # Persistenza FAISS
    persist_dir: str = "faiss_index_example"
    # Text splitting
    chunk_size: int = 700
    chunk_overlap: int = 100
    # Retriever (MMR)
    search_type: str = "mmr"        # "mmr" o "similarity"
    k: int = 6                      # risultati finali
    fetch_k: int = 20               # candidati iniziali (per MMR)
    mmr_lambda: float = 0.7         # 0 = diversificazione massima, 1 = pertinenza massima
    # Embedding
    embedding_model_name: str = "text-embedding-ada-002"  # Azure deployment name



SETTINGS = Settings()


# =========================
# Componenti di base
# =========================

def get_embeddings(settings: Settings):
    """
    Restituisce un modello di embedding di Azure OpenAI.
    """
    embeddings = AzureOpenAIEmbeddings(
        model=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME", settings.embedding_model_name),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")
    )
    return embeddings


def llm():
    """
    Inizializza un ChatModel puntando a Azure OpenAI.
    Richiede:
      - AZURE_OPENAI_ENDPOINT
      - AZURE_OPENAI_API_KEY  
      - AZURE_OPENAI_API_VERSION
      - MODEL (deployment name)
    """
    return AzureChatOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01"),
        azure_deployment=os.getenv("MODEL"),
        temperature=0.1
    )


def corpus() -> List[Document]:
    """
    Crea un piccolo corpus di documenti in inglese con metadati e 'source' per citazioni.
    """
    docs_path = Path(__file__).parent / "docs"
    documents = []
    for doc_path in docs_path.glob("*.md"):
        with open(doc_path, "r", encoding="utf-8") as f:
            content = f.read()
            documents.append(Document(page_content=content, metadata={"source": doc_path.name}))
    return documents


def split_documents(docs: List[Document], settings: Settings) -> List[Document]:
    """
    Applica uno splitting robusto ai documenti per ottimizzare il retrieval.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=[
            "\n\n", "\n", ". ", "? ", "! ", "; ", ": ",
            ", ", " ", ""
        ],
    )
    return splitter.split_documents(docs)


def build_faiss_vectorstore(chunks: List[Document], embeddings, persist_dir: str) -> FAISS:
    """
    Costruisce da zero un FAISS index (IndexFlatL2) e lo salva su disco.
    """
    # Determina la dimensione dell'embedding
    vs = FAISS.from_documents(
        documents=chunks,
        embedding=embeddings
    )

    Path(persist_dir).mkdir(parents=True, exist_ok=True)
    vs.save_local(persist_dir)
    return vs


def load_or_build_vectorstore(settings: Settings, embeddings, docs: List[Document]) -> FAISS:
    """
    Tenta il load di un indice FAISS persistente; se non esiste, lo costruisce e lo salva.
    """
    persist_path = Path(settings.persist_dir)
    index_file = persist_path / "index.faiss"
    meta_file = persist_path / "index.pkl"

    if index_file.exists() and meta_file.exists():
        return FAISS.load_local(
            settings.persist_dir,
            embeddings,
            allow_dangerous_deserialization=True
        )

    chunks = split_documents(docs, settings)
    return build_faiss_vectorstore(chunks, embeddings, settings.persist_dir)


def make_retriever(vector_store: FAISS, settings: Settings):
    """
    Configura il retriever. Con 'mmr' otteniamo risultati meno ridondanti e più coprenti.
    """
    if settings.search_type == "mmr":
        return vector_store.as_retriever(
            search_type="mmr",
            search_kwargs={"k": settings.k, "fetch_k": settings.fetch_k, "lambda_mult": settings.mmr_lambda},
        )
    else:
        return vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": settings.k},
        )


def format_docs_for_prompt(docs: List[Document]) -> str:
    """
    Prepara il contesto per il prompt, includendo citazioni [source].
    """
    lines = []
    for i, d in enumerate(docs, start=1):
        src = d.metadata.get("source", f"doc{i}")
        lines.append(f"[source:{src}] {d.page_content}")
    return "\n\n".join(lines)


def build_rag_chain(llm, retriever):
    """
    Builds the RAG chain (retrieval -> prompt -> LLM) with citations and anti-hallucination rules.
    """
    system_prompt = (
        "You are an expert assistant. Respond in English. "
        "Use ONLY the CONTENT provided in the context. "
        "If information is not present, state that it's not available. "
        "Include citations in square brackets in the format [source:...]. "
        "Be concise, accurate and technically correct."
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human",
         "Question:\n{question}\n\n"
         "Context (selected extracts):\n{context}\n\n"
         "Instructions:\n"
         "1) Answer only with information contained in the context.\n"
         "2) Always cite relevant sources in the format [source:FILE].\n"
         "3) If the answer is not in the context, write: 'No relevant information found in the provided context.'")
    ])

    # LCEL: dict -> prompt -> llm -> parser
    chain = (
        {
            "context": retriever | format_docs_for_prompt,
            "question": RunnablePassthrough(),
        }
        | prompt
        | llm
        | StrOutputParser()
    )
    return chain


def rag_answer(question: str, chain) -> str:
    """
    Esegue la catena RAG per una singola domanda.
    """
    return chain.invoke(question)



def main():
    settings = SETTINGS

    # 1) Componenti
    embeddings = get_embeddings(settings)
    llm_model = llm()

    # 2) Dati simulati e indicizzazione (load or build)
    docs = corpus()
    vector_store = load_or_build_vectorstore(settings, embeddings, docs)

    # 3) Retriever ottimizzato
    retriever = make_retriever(vector_store, settings)

    # 4) Catena RAG
    chain = build_rag_chain(llm_model, retriever)

    # 5) Esempi di domande
    questions = [
        "Che cos'è una pipeline RAG e quali sono le sue fasi principali?",
        "A cosa serve FAISS e quali capacità offre?",
        "Cos'è MMR e perché è utile durante il retrieval?",
        "Quale dimensione hanno gli embedding prodotti da all-MiniLM-L6-v2?"
    ]

    for q in questions:
        print("=" * 80)
        print("Q:", q)
        print("-" * 80)
        ans = rag_answer(q, chain)
        print(ans)
        print()

if __name__ == "__main__":
    main()