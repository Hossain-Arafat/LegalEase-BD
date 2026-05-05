# rebuild_bm25.py
import json
import pickle
from rank_bm25 import BM25Okapi

DATA_DIR = "G:/LegalEase-BD/legalease_modal/data"

print("Loading chunks...")
with open(f"{DATA_DIR}/chunks/Acts_english.json", "r", encoding="utf-8") as f:
    en_data = json.load(f)
with open(f"{DATA_DIR}/chunks/Acts_bengali.json", "r", encoding="utf-8") as f:
    bn_data = json.load(f)

# Extract English chunks
en_chunks = []
for act in en_data.get("acts", []):
    for section in act.get("sections", []):
        text = section.get("section_content", "")
        if len(text) > 50:
            en_chunks.append({
                "text": text,
                "metadata": {
                    "act_title": act.get("act_title", "Unknown"),
                    "act_no": act.get("act_no", ""),
                    "act_year": act.get("act_year", ""),
                    "section_label": f"Section {section.get('section_number', '')}" if isinstance(section, dict) else "General",
                    "language": "en"
                }
            })

# Extract Bengali chunks
bn_chunks = []
for act in bn_data.get("acts", []):
    for section in act.get("sections", []):
        text = section.get("section_content", "")
        if len(text) > 50:
            bn_chunks.append({
                "text": text,
                "metadata": {
                    "act_title": act.get("act_title", "Unknown"),
                    "act_no": act.get("act_no", ""),
                    "act_year": act.get("act_year", ""),
                    "section_label": f"Section {section.get('section_number', '')}" if isinstance(section, dict) else "General",
                    "language": "bn"
                }
            })

print(f"English chunks: {len(en_chunks)}")
print(f"Bengali chunks: {len(bn_chunks)}")

# Tokenize for BM25 (works for both English and Bengali text)
print("Tokenizing...")
corpus = []
all_chunks = []

# Add English chunks
for chunk in en_chunks:
    # Simple tokenization - split on whitespace
    tokens = chunk["text"].split()
    corpus.append(tokens)
    all_chunks.append(chunk)

# Add Bengali chunks
for chunk in bn_chunks:
    tokens = chunk["text"].split()
    corpus.append(tokens)
    all_chunks.append(chunk)

print(f"Total chunks for BM25: {len(all_chunks)}")

# Build BM25
print("Building BM25 index...")
bm25 = BM25Okapi(corpus)

# Save
print("Saving...")
with open(f"{DATA_DIR}/indexes/bm25_final.pkl", "wb") as f:
    pickle.dump({
        "bm25": bm25,
        "en_chunks": all_chunks,  # Store all chunks together
        "bn_chunks": []  # Keep for compatibility
    }, f)

print(f"✅ BM25 saved with {len(all_chunks)} total chunks")