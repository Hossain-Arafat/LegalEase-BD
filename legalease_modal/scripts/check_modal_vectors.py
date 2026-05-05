# check_modal_vectors.py
import modal

app = modal.App("check-vectors")
volume = modal.Volume.from_name("legalease-data")

image = modal.Image.debian_slim().pip_install("chromadb")

@app.function(volumes={"/data": volume}, image=image)
def check_vectors():
    import chromadb
    import os
    
    print("Files in /data/indexes/chroma_db:", os.listdir("/data/indexes/chroma_db")[:10])
    
    client = chromadb.PersistentClient("/data/indexes/chroma_db")
    collections = client.list_collections()
    print(f"Collections: {[c.name for c in collections]}")
    
    if collections:
        col = client.get_collection(collections[0].name)
        print(f"Vector count: {col.count()}")
        return col.count()
    return 0

@app.local_entrypoint()
def main():
    count = check_vectors.remote()
    print(f"✅ Total vectors in Modal: {count}")