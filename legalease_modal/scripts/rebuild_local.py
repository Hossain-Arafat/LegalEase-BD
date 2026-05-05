# rebuild_local.py
import json
import os
import shutil
import chromadb
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

DATA_DIR = "G:/LegalEase-BD/legalease_modal/data"

print("Loading chunks...")
with open(os.path.join(DATA_DIR, "chunks", "Acts_english.json"), "r", encoding="utf-8") as f:
    en_data = json.load(f)
with open(os.path.join(DATA_DIR, "chunks", "Acts_bengali.json"), "r", encoding="utf-8") as f:
    bn_data = json.load(f)

# Handle both list and dict formats
if isinstance(en_data, dict):
    en_chunks = list(en_data.values())
else:
    en_chunks = en_data

if isinstance(bn_data, dict):
    bn_chunks = list(bn_data.values())
else:
    bn_chunks = bn_data

# Flatten if nested
if en_chunks and isinstance(en_chunks[0], dict) and "chunks" in en_chunks[0]:
    en_chunks = en_chunks[0]["chunks"]
if bn_chunks and isinstance(bn_chunks[0], dict) and "chunks" in bn_chunks[0]:
    bn_chunks = bn_chunks[0]["chunks"]

all_chunks = []
if isinstance(en_chunks, list):
    all_chunks.extend(en_chunks)
if isinstance(bn_chunks, list):
    all_chunks.extend(bn_chunks)

print(f"Total chunks: {len(all_chunks)}")
print(f"Sample chunk: {all_chunks[0].keys() if all_chunks else 'No chunks'}")

# Continue with the rest...
print("Loading embedding model...")
model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

# Delete old ChromaDB
chroma_path = os.path.join(DATA_DIR, "indexes", "chroma_db")
if os.path.exists(chroma_path):
    shutil.rmtree(chroma_path)
    print("Removed old ChromaDB")

print("Creating new ChromaDB...")
client = chromadb.PersistentClient(path=chroma_path)
collection = client.create_collection("legalease_final")

BATCH_SIZE = 100
print("Adding vectors...")

for i in tqdm(range(0, len(all_chunks), BATCH_SIZE)):
    batch = all_chunks[i:i+BATCH_SIZE]
    texts = []
    metadatas = []
    ids = []
    
    for j, chunk in enumerate(batch):
        # Handle different chunk structures
        if isinstance(chunk, dict):
            text = chunk.get("text", chunk.get("content", str(chunk)))
            meta = chunk.get("metadata", chunk)
            chunk_id = meta.get("chunk_id", f"chunk_{i}_{j}")
        else:
            text = str(chunk)
            meta = {}
            chunk_id = f"chunk_{i}_{j}"
        
        texts.append(text)
        metadatas.append({
            "act_title": str(meta.get("act_title", ""))[:200],
            "act_no": str(meta.get("act_no", ""))[:50],
            "act_year": str(meta.get("act_year", ""))[:20],
            "section_label": str(meta.get("section_label", ""))[:100],
            "language": str(meta.get("language", "en")),
        })
        ids.append(chunk_id)
    
    embeddings = model.encode(texts, normalize_embeddings=True).tolist()
    collection.add(documents=texts, embeddings=embeddings, metadatas=metadatas, ids=ids)

print(f"Done! Total vectors: {collection.count()}")