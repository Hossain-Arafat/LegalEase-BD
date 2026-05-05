# build_indexes.py - Fixed for dictionary format
import json
import os
import pickle
import re
from tqdm import tqdm

# Install packages first if needed:
# pip install rank_bm25 sentence-transformers chromadb tqdm

import chromadb
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi

# ============================================
# CONFIGURATION - UPDATE THESE PATHS
# ============================================

# Where your JSON chunk files are
DATA_DIR = "G:/LegalEase-BD/legalease_modal/data"

# Create directories
CHUNKS_DIR = f"{DATA_DIR}/chunks"
INDEXES_DIR = f"{DATA_DIR}/indexes"

# Create directories if they don't exist
os.makedirs(INDEXES_DIR, exist_ok=True)
os.makedirs(CHUNKS_DIR, exist_ok=True)

# Your JSON files
EN_CHUNKS_FILE = f"{CHUNKS_DIR}/Acts_english.json"
BN_CHUNKS_FILE = f"{CHUNKS_DIR}/Acts_bengali.json"

# ============================================
# CHECK IF FILES EXIST
# ============================================

print("🔍 Checking for chunk files...")
if not os.path.exists(EN_CHUNKS_FILE):
    print(f"❌ English chunks not found at: {EN_CHUNKS_FILE}")
    exit(1)

if not os.path.exists(BN_CHUNKS_FILE):
    print(f"❌ Bengali chunks not found at: {BN_CHUNKS_FILE}")
    exit(1)

print("✅ Found both chunk files!")

# ============================================
# LOAD AND FIX THE DATA STRUCTURE
# ============================================

print("\n📚 Loading chunks...")

with open(EN_CHUNKS_FILE, "r", encoding="utf-8") as f:
    en_data = json.load(f)

with open(BN_CHUNKS_FILE, "r", encoding="utf-8") as f:
    bn_data = json.load(f)

# Check what structure we have
print(f"   English data type: {type(en_data)}")
print(f"   Bengali data type: {type(bn_data)}")

# Convert to list if it's a dict
if isinstance(en_data, dict):
    print("   Converting English dict to list...")
    # Check if it's like {"chunks": [...]} or just a dict of chunks
    if "chunks" in en_data:
        en_chunks = en_data["chunks"]
    else:
        # Try to get all values from dict
        en_chunks = list(en_data.values()) if isinstance(list(en_data.values())[0], dict) else en_data
else:
    en_chunks = en_data

if isinstance(bn_data, dict):
    print("   Converting Bengali dict to list...")
    if "chunks" in bn_data:
        bn_chunks = bn_data["chunks"]
    else:
        bn_chunks = list(bn_data.values()) if isinstance(list(bn_data.values())[0], dict) else bn_data
else:
    bn_chunks = bn_data

# Ensure they're lists
if not isinstance(en_chunks, list):
    en_chunks = [en_chunks]
if not isinstance(bn_chunks, list):
    bn_chunks = [bn_chunks]

all_chunks = en_chunks + bn_chunks
print(f"✅ Loaded {len(en_chunks)} English chunks, {len(bn_chunks)} Bengali chunks")
print(f"   Total: {len(all_chunks)} chunks")

# Show a sample to verify
if len(all_chunks) > 0:
    print(f"\n📝 Sample chunk structure:")
    sample = all_chunks[0]
    print(f"   Type: {type(sample)}")
    if isinstance(sample, dict):
        print(f"   Keys: {list(sample.keys())[:5]}")
    else:
        print(f"   Content: {str(sample)[:100]}")

# ============================================
# LEGAL STOPWORDS
# ============================================

LEGAL_STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to",
    "for", "of", "with", "by", "from", "as", "is", "are", "was",
    "were", "be", "been", "being", "have", "has", "had", "do", "does",
    "did", "will", "would", "could", "should", "may", "might",
    "can", "this", "that", "these", "those", "it", "its", "not",
    "act", "rules", "section", "clause", "provisions",
    "under", "pursuant", "hereby", "herein", "notwithstanding",
}

def tokenize_en(text):
    """Tokenize English text for BM25"""
    if not isinstance(text, str):
        text = str(text)
    text = re.sub(r"[^a-z0-9\s]", " ", text.lower())
    return [t for t in text.split() if t not in LEGAL_STOPWORDS and len(t) > 2]

# ============================================
# STEP 2: Build BM25 Index (English only)
# ============================================

print("\n📊 Building BM25 index for English chunks...")
print("   Tokenizing chunks...")

corpus = []
valid_chunks = []

for c in tqdm(en_chunks, desc="Tokenizing"):
    # Extract text from chunk - handle different formats
    if isinstance(c, dict):
        text = c.get("text", c.get("content", str(c)))
    else:
        text = str(c)
    
    tokens = tokenize_en(text)
    if tokens:  # Only add if we have tokens
        corpus.append(tokens)
        valid_chunks.append(c)

print(f"   Tokenized {len(corpus)} valid chunks (filtered out {len(en_chunks) - len(corpus)} empty)")

if len(corpus) == 0:
    print("❌ No valid chunks for BM25! Check your data format.")
    exit(1)

print("   Building BM25 model...")
bm25 = BM25Okapi(corpus)

# Save BM25 with chunks
bm25_path = f"{INDEXES_DIR}/bm25_final.pkl"
with open(bm25_path, "wb") as f:
    pickle.dump({
        "bm25": bm25,
        "en_chunks": valid_chunks,
        "bn_chunks": bn_chunks,
    }, f)
print(f"✅ BM25 saved to {bm25_path}")
print(f"   File size: {os.path.getsize(bm25_path) / 1024 / 1024:.1f} MB")

# ============================================
# STEP 3: Build ChromaDB Index
# ============================================

print("\n🔤 Building ChromaDB embedding index...")
print("   Loading embedding model (this may take a moment)...")

# Load embedding model (using CPU to avoid CUDA issues on Windows)
model = SentenceTransformer(
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    device="cpu"
)
model.max_seq_length = 512
print("   ✅ Model loaded")

# Create ChromaDB
chroma_path = f"{INDEXES_DIR}/chroma_db"
print(f"   Creating ChromaDB at: {chroma_path}")

# Clean up old if exists
import shutil
if os.path.exists(chroma_path):
    print("   Removing old ChromaDB...")
    shutil.rmtree(chroma_path)

client = chromadb.PersistentClient(path=chroma_path)
collection = client.create_collection(
    "legalease_final",
    metadata={"hnsw:space": "cosine"}
)

# Embed in batches
BATCH_SIZE = 50  # Smaller batch for Windows
print(f"   Embedding {len(all_chunks)} chunks in batches of {BATCH_SIZE}...")
print("   This will take 15-30 minutes...")

# Prepare all texts and metadata
all_texts = []
all_metadatas = []
all_ids = []

for c in all_chunks:
    if isinstance(c, dict):
        # Extract text
        text = c.get("text", c.get("content", str(c)))
        all_texts.append(text)
        
        # Extract metadata
        m = c.get("metadata", c)
        all_metadatas.append({
            "act_title": str(m.get("act_title", ""))[:200],
            "act_no": str(m.get("act_no", ""))[:50],
            "act_year": str(m.get("act_year", ""))[:20],
            "act_id": str(m.get("act_id", ""))[:100],
            "section_label": str(m.get("section_label", ""))[:100],
            "language": str(m.get("language", "en"))[:10],
            "raw_text": str(m.get("raw_text", text))[:1000],
        })
        
        # Create ID
        chunk_id = m.get("chunk_id", f"chunk_{len(all_ids)}")
        all_ids.append(str(chunk_id))
    else:
        all_texts.append(str(c))
        all_metadatas.append({"act_title": "Unknown", "language": "en"})
        all_ids.append(f"chunk_{len(all_ids)}")

# Batch add to ChromaDB
for i in tqdm(range(0, len(all_texts), BATCH_SIZE), desc="Embedding"):
    batch_texts = all_texts[i:i+BATCH_SIZE]
    batch_metadatas = all_metadatas[i:i+BATCH_SIZE]
    batch_ids = all_ids[i:i+BATCH_SIZE]
    
    # Generate embeddings
    embeddings = model.encode(
        batch_texts,
        normalize_embeddings=True,
        show_progress_bar=False,
        batch_size=BATCH_SIZE
    ).tolist()
    
    # Add to ChromaDB
    collection.add(
        documents=batch_texts,
        embeddings=embeddings,
        metadatas=batch_metadatas,
        ids=batch_ids,
    )

print(f"✅ ChromaDB saved to {chroma_path}")
print(f"   Total vectors: {collection.count()}")

# Calculate size
total_size = 0
for dirpath, dirnames, filenames in os.walk(chroma_path):
    for f in filenames:
        fp = os.path.join(dirpath, f)
        total_size += os.path.getsize(fp)
print(f"   Database size: {total_size / 1024 / 1024 / 1024:.2f} GB")

# ============================================
# SUMMARY
# ============================================

print("\n" + "="*50)
print("🎉 INDEXING COMPLETE!")
print("="*50)
print(f"\nBM25 index:     {bm25_path}")
print(f"ChromaDB:       {chroma_path}")
print(f"\nTotal vectors:  {collection.count()}")

print("\n📤 Next step - Upload to Modal:")
print(f"modal volume put legalease-data /legalease_data/indexes {INDEXES_DIR}")