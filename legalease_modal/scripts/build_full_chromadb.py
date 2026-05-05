# build_full_chromadb.py
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

# Extract chunks from your JSON structure
# Your JSON has {"dataset_info": {...}, "acts": [...]}
en_chunks = []
for act in en_data.get("acts", []):
    for section in act.get("sections", []):
        section_text = section.get("section_content", "") if isinstance(section, dict) else str(section)
        if len(section_text) > 50:  # Only keep non-empty sections
            en_chunks.append({
                "text": section_text,
                "metadata": {
                    "act_title": act.get("act_title", "Unknown"),
                    "language": "en"
                }
            })

bn_chunks = []
for act in bn_data.get("acts", []):
    for section in act.get("sections", []):
        section_text = section.get("section_content", "") if isinstance(section, dict) else str(section)
        if len(section_text) > 50:
            bn_chunks.append({
                "text": section_text,
                "metadata": {
                    "act_title": act.get("act_title", "Unknown"),
                    "language": "bn"
                }
            })

all_chunks = en_chunks + bn_chunks
print(f"Total chunks to embed: {len(all_chunks)}")

# Load model
print("Loading embedding model...")
model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

# Delete old ChromaDB
chroma_path = os.path.join(DATA_DIR, "indexes", "chroma_db")
if os.path.exists(chroma_path):
    shutil.rmtree(chroma_path)
    print("Removed old ChromaDB")

# Create new ChromaDB
print("Creating ChromaDB...")
client = chromadb.PersistentClient(path=chroma_path)
collection = client.create_collection("legalease_final")

BATCH_SIZE = 100
print("Adding vectors...")

for i in tqdm(range(0, len(all_chunks), BATCH_SIZE)):
    batch = all_chunks[i:i+BATCH_SIZE]
    texts = [c["text"] for c in batch]
    embeddings = model.encode(texts, normalize_embeddings=True).tolist()
    
    metadatas = []
    ids = []
    for j, c in enumerate(batch):
        metadatas.append({
            "act_title": c["metadata"].get("act_title", "")[:200],
            "language": c["metadata"].get("language", "en"),
        })
        ids.append(f"chunk_{i}_{j}")
    
    collection.add(
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
    )

print(f"✅ Done! Total vectors: {collection.count()}")