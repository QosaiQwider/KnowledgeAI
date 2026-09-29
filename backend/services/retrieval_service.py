from sqlalchemy.orm import Session

from database.database_models import (
    DocumentChunk,
    Document
)

from services.embedding_service import generate_embedding


# =========================================================
# SEARCH CHUNKS
# =========================================================

def search_chunks(
    db: Session,
    kb_id: int,
    query: str,
    limit: int = 5
):
    """
    Search for the most relevant document chunks
    inside a specific Knowledge Base.

    Steps:
    1. Convert the user's question into an embedding.
    2. Compare it with stored chunk embeddings.
    3. Filter results to the selected Knowledge Base.
    4. Return the closest chunks.
    """

    # =====================================================
    # 1. GENERATE QUERY EMBEDDING
    # =====================================================

    query_embedding = generate_embedding(query)

    if query_embedding is None:
        return []


    # =====================================================
    # 2. CALCULATE COSINE DISTANCE
    # =====================================================

    distance = (
        DocumentChunk.embedding
        .cosine_distance(query_embedding)
        .label("distance")
    )


    # =====================================================
    # 3. SEARCH INSIDE THE SELECTED KNOWLEDGE BASE ONLY
    # =====================================================

    results = (
        db.query(
            DocumentChunk,
            Document,
            distance
        )

        .join(
            Document,
            DocumentChunk.document_id == Document.Document_ID
        )

        .filter(
            Document.KB_ID == kb_id,

            # Ignore old chunks that don't have embeddings
            DocumentChunk.embedding.isnot(None)
        )

        .order_by(
            distance
        )

        .limit(limit)

        .all()
    )


    # =====================================================
    # 4. FORMAT RESULTS
    # =====================================================

    formatted_results = []


    for chunk, document, chunk_distance in results:

        formatted_results.append(
            {
                "chunk_id": chunk.DocumentChunk_ID,

                "document_id": document.Document_ID,

                "file_name": document.file_name,

                "content": chunk.content,

                "page_number": chunk.page_number,

                "chunk_index": chunk.chunk_index,

                "distance": float(chunk_distance)
            }
        )


    return formatted_results