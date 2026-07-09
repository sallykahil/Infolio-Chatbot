"""
infolio RAG API
Multi-tenant RAG backend for small businesses.
Endpoints: /upload-docs, /ingest-url, /ask, /tenants
Compatible with langchain 1.x + langchain-qdrant
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os, shutil, tempfile

from dotenv import load_dotenv
load_dotenv()

# === Document loaders ===
from langchain_community.document_loaders import PDFPlumberLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings

# === Vector store (Qdrant) ===
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from langchain_qdrant import QdrantVectorStore

# === LLM (Groq) ===
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# === Web scraping ===
import requests
from bs4 import BeautifulSoup

# ─────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────
GROQ_API_KEY   = os.getenv("GROQ_API_KEY")
QDRANT_URL     = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", None)
EMBED_MODEL    = os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")
TOP_K          = int(os.getenv("TOP_K", "3"))

app = FastAPI(title="infolio RAG API", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────
# Shared clients
# ─────────────────────────────────────────────
embeddings = HuggingFaceEmbeddings(
    model_name=EMBED_MODEL,
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)

qdrant_client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model="llama-3.3-70b-versatile",
    temperature=0.2,
)

splitter = RecursiveCharacterTextSplitter(
    chunk_size=700,
    chunk_overlap=80,
    separators=["\n\n", "\n", ". ", " ", ""],
)

PROMPT = PromptTemplate.from_template("""You are a helpful assistant for a small business.
Use ONLY the context below to answer. If the answer isn't in the context, say:
"I don't have that information — please contact us directly."
Be concise, friendly, and helpful.

Context:
{context}

Question: {question}

Answer:""")


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────
def get_or_create_collection(tenant_id: str):
    collection_name = f"biz_{tenant_id}"
    existing = [c.name for c in qdrant_client.get_collections().collections]
    if collection_name not in existing:
        qdrant_client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE),
        )
    return collection_name


def index_documents(docs: list[Document], tenant_id: str):
    chunks = splitter.split_documents(docs)
    collection_name = get_or_create_collection(tenant_id)
    QdrantVectorStore.from_documents(
        chunks,
        embeddings,
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
        collection_name=collection_name,
        force_recreate=False,
    )
    return len(chunks)


def get_rag_chain(tenant_id: str):
    collection_name = f"biz_{tenant_id}"
    vectorstore = QdrantVectorStore(
        client=qdrant_client,
        collection_name=collection_name,
        embedding=embeddings,
    )
    retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={"k": TOP_K},
    )

    def format_docs(docs):
        return "\n\n".join(d.page_content for d in docs)

    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | PROMPT
        | llm
        | StrOutputParser()
    )
    return chain


# ─────────────────────────────────────────────
# Request models
# ─────────────────────────────────────────────
class IngestURLRequest(BaseModel):
    tenant_id: str
    url: str

class AskRequest(BaseModel):
    tenant_id: str
    question: str

class AskResponse(BaseModel):
    answer: str
    tenant_id: str


# ─────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────
@app.get("/")
def root():
    return {"status": "infolio RAG API running ✓"}


@app.get("/dashboard")
def dashboard():
    return FileResponse(os.path.join(os.path.dirname(__file__), "dashboard.html"))


@app.post("/upload-docs")
async def upload_docs(tenant_id: str, files: list[UploadFile] = File(...)):
    total_chunks = 0
    with tempfile.TemporaryDirectory() as tmp:
        for file in files:
            if not file.filename.endswith(".pdf"):
                raise HTTPException(400, f"{file.filename} is not a PDF")
            path = os.path.join(tmp, file.filename)
            with open(path, "wb") as f:
                shutil.copyfileobj(file.file, f)
            loader = PDFPlumberLoader(path)
            docs = loader.load()
            total_chunks += index_documents(docs, tenant_id)
    return {"tenant_id": tenant_id, "chunks_indexed": total_chunks, "files": len(files)}


@app.post("/ingest-url")
def ingest_url(req: IngestURLRequest):
    try:
        resp = requests.get(req.url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        raise HTTPException(400, f"Could not fetch URL: {e}")

    soup = BeautifulSoup(resp.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    text = soup.get_text(separator="\n", strip=True)

    if len(text) < 100:
        raise HTTPException(400, "Page has too little text to index.")

    docs = [Document(page_content=text, metadata={"source": req.url})]
    chunks = index_documents(docs, req.tenant_id)
    return {"tenant_id": req.tenant_id, "url": req.url, "chunks_indexed": chunks}


@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    collection_name = f"biz_{req.tenant_id}"
    existing = [c.name for c in qdrant_client.get_collections().collections]
    if collection_name not in existing:
        raise HTTPException(404, f"No data for tenant '{req.tenant_id}'. Upload docs first.")

    chain = get_rag_chain(req.tenant_id)
    answer = chain.invoke(req.question)
    return AskResponse(answer=answer, tenant_id=req.tenant_id)


@app.get("/tenants")
def list_tenants():
    collections = [
        c.name.replace("biz_", "")
        for c in qdrant_client.get_collections().collections
        if c.name.startswith("biz_")
    ]
    return {"tenants": collections, "count": len(collections)} 
