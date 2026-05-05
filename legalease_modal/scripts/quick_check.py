# quick_check.py
import pickle

with open("G:/LegalEase-BD/legalease_modal/data/indexes/bm25_final.pkl", "rb") as f:
    data = pickle.load(f)
    
print(f"BM25 chunks: {len(data.get('en_chunks', []))}")