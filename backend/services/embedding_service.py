from sentence_transformers import SentenceTransformer


# =========================================================
# EMBEDDING MODEL
# =========================================================

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Use the model already downloaded on the device.
# This prevents Hugging Face from checking the internet
# every time the backend starts.
model = SentenceTransformer(
    MODEL_NAME,
    local_files_only=True
)


# =========================================================
# GENERATE EMBEDDING
# =========================================================

def generate_embedding(text: str):

    if not text or not text.strip():
        return None

    embedding = model.encode(
        text,
        normalize_embeddings=True
    )

    return embedding.tolist()