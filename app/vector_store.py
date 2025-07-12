import chromadb

chroma_client = chromadb.Client()
model = None

def get_model():
    global model
    if model is None:
        try:
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            print(f"[ERROR] Could not load SentenceTransformer: {e}")
            model = None
    return model

COLLECTION_NAME = "documents"

# Ensure collection exists
if not chroma_client.list_collections() or COLLECTION_NAME not in [c.name for c in chroma_client.list_collections()]:
    chroma_client.create_collection(COLLECTION_NAME)
collection = chroma_client.get_collection(COLLECTION_NAME)

def add_to_vector_store(chunks, metadatas=None):
    try:
        if not chunks:
            print("[WARNING] No chunks provided to vector store")
            return
        model_instance = get_model()
        if model_instance is None:
            print("[ERROR] Embedding model not available.")
            return
        embeddings = model_instance.encode(chunks).tolist()
        ids = [f"chunk_{i}" for i in range(len(chunks))]
        collection.add(documents=chunks, embeddings=embeddings, ids=ids, metadatas=metadatas)
        print(f"[INFO] Added {len(chunks)} chunks to vector store")
    except Exception as e:
        print(f"[ERROR] Failed to add chunks to vector store: {e}")
        # Don't raise the exception to prevent the entire upload from failing

def similarity_search(query, top_k=5):
    try:
        if not query or not query.strip():
            return {"documents": [[]], "metadatas": [[]], "distances": [[]]}
        model_instance = get_model()
        if model_instance is None:
            print("[ERROR] Embedding model not available.")
            return {"documents": [[]], "metadatas": [[]], "distances": [[]]}
        embedding = model_instance.encode([query]).tolist()[0]
        results = collection.query(query_embeddings=[embedding], n_results=top_k)
        return results
    except Exception as e:
        print(f"[ERROR] Similarity search failed: {e}")
        # Return empty results instead of failing
        return {"documents": [[]], "metadatas": [[]], "distances": [[]]} 