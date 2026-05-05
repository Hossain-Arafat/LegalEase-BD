# legalease_complete.py - Everything in one file that actually works
import modal
from modal import App, Image, Volume, method, enter

app = modal.App("legalease-bd")

# ============================================================
# IMAGE with everything needed
# ============================================================

image = Image.debian_slim().pip_install(
    "fastapi",
    "uvicorn", 
    "pydantic",
    "sentence-transformers",
    "chromadb",
    "rank-bm25",
    "numpy==1.23.5",
)

# ============================================================
# VOLUME for data
# ============================================================

volume = Volume.from_name("legalease-data", create_if_missing=True)

# ============================================================
# YOUR LLM CLASS (runs on Modal's GPU)
# ============================================================

@app.cls(
    image=image,
    volumes={"/data": volume},
    scaledown_window=300,
    memory=8192,
    gpu="T4",  # GPU for faster embeddings
)
class LegalEaseLLM:
    
    @enter()
    def load(self):
        from sentence_transformers import SentenceTransformer
        import chromadb
        import pickle
        
        print("🚀 Loading LegalEase BD on Modal GPU...")
        
        # Load embedder
        self.embedder = SentenceTransformer(
            "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )
        
        # Load ChromaDB
        self.chroma = chromadb.PersistentClient("/data/indexes/chroma_db")
        self.collection = self.chroma.get_collection("legalease_final")
        
        print("✅ Ready to answer questions!")
    
    @method()
    def search(self, question: str, top_k: int = 3) -> dict:
        """Search legal documents - this runs on Modal GPU"""
        emb = self.embedder.encode(question, normalize_embeddings=True).tolist()
        results = self.collection.query(
            query_embeddings=[emb],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )
        
        return {
            "question": question,
            "sources": results["documents"][0],
            "metadata": results["metadatas"][0],
            "scores": [1 - d for d in results["distances"][0]]
        }

# ============================================================
# FASTAPI - Exposes your LLM as a web API
# ============================================================

web_app = modal.asgi_app(
    image=image,
    volumes={"/data": volume},
)

@web_app.get("/")
async def root():
    return {"service": "LegalEase BD", "status": "running"}

@web_app.post("/query")
async def query(request: dict):
    from pydantic import BaseModel
    
    class QueryRequest(BaseModel):
        query: str
    
    req = QueryRequest(**request)
    
    # Create instance of your LLM and call it
    llm = LegalEaseLLM()
    result = await llm.search.remote.aio(req.query)
    
    # Format response
    response_text = f"Found {len(result['sources'])} sources:\n\n"
    for i, (src, meta, score) in enumerate(zip(
        result['sources'], result['metadata'], result['scores']
    ), 1):
        act = meta.get('act_title', 'Unknown')
        response_text += f"[{i}] {act} (relevance: {score:.2%})\n"
        response_text += f"{src[:200]}...\n\n"
    
    return {
        "query": req.query,
        "response": response_text,
        "sources": result['sources'][:3]
    }