# inspect_volume.py
import modal

app = modal.App("inspect-volume")
volume = modal.Volume.from_name("legalease-data")

# Add image with dependencies
image = modal.Image.debian_slim().pip_install("chromadb")

@app.function(volumes={"/data": volume}, image=image)
def inspect():
    import os
    import chromadb
    
    print("=== Volume Contents ===")
    print("Files in /data:", os.listdir("/data"))
    
    if os.path.exists("/data/indexes"):
        print("Files in /data/indexes:", os.listdir("/data/indexes"))
    
    if os.path.exists("/data/indexes/chroma_db"):
        print("Files in /data/indexes/chroma_db:", os.listdir("/data/indexes/chroma_db")[:10])
    
    print("\n=== ChromaDB Collections ===")
    client = chromadb.PersistentClient("/data/indexes/chroma_db")
    collections = client.list_collections()
    print(f"Number of collections: {len(collections)}")
    for c in collections:
        print(f"  - {c.name}: {c.count()} vectors")
    
    return [c.name for c in collections]

@app.local_entrypoint()
def main():
    print("Starting inspection...")
    result = inspect.remote()
    print(f"Collections found: {result}")