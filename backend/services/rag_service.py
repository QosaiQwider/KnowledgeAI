from sqlalchemy.orm import Session

from services.retrieval_service import search_chunks
from services.llm_service import generate_answer


# =========================================================
# SETTINGS
# =========================================================

TOP_K = 5

# Smaller cosine distance = more relevant
DISTANCE_THRESHOLD = 0.70


# =========================================================
# RAG ANSWER
# =========================================================

def ask_rag(
    db: Session,
    kb_id: int,
    question: str
):

    # -----------------------------------------------------
    # 1. Validate question
    # -----------------------------------------------------

    if not question or not question.strip():
        return {
            "answer": "Please enter a question.",
            "sources": []
        }


    # -----------------------------------------------------
    # 2. Retrieve relevant chunks
    # -----------------------------------------------------

    results = search_chunks(
        db=db,
        kb_id=kb_id,
        query=question,
        limit=TOP_K
    )


    # -----------------------------------------------------
    # 3. No chunks found
    # -----------------------------------------------------

    if not results:
        return {
            "answer": (
                "I couldn't find an answer to this question "
                "in the uploaded documents."
            ),
            "sources": []
        }


    # -----------------------------------------------------
    # 4. Filter irrelevant chunks
    # -----------------------------------------------------

    relevant_results = [
        result
        for result in results
        if result["distance"] <= DISTANCE_THRESHOLD
    ]


    # -----------------------------------------------------
    # 5. Nothing relevant enough
    # -----------------------------------------------------

    if not relevant_results:
        return {
            "answer": (
                "I couldn't find an answer to this question "
                "in the uploaded documents."
            ),
            "sources": []
        }


    # -----------------------------------------------------
    # 6. Build document context
    # -----------------------------------------------------

    context_parts = []

    for index, result in enumerate(
        relevant_results,
        start=1
    ):

        source_text = (
            f"[SOURCE {index}]\n"
            f"File: {result['file_name']}\n"
            f"Page: {result['page_number']}\n"
            f"Content:\n"
            f"{result['content']}"
        )

        context_parts.append(source_text)


    context = "\n\n".join(context_parts)


    # -----------------------------------------------------
    # 7. Build grounded prompt
    # -----------------------------------------------------

    prompt = f"""
You are a document question-answering assistant.

Answer the user's question using ONLY the information contained
in the provided document context.

Rules:

1. Do not use outside knowledge.
2. Do not invent information.
3. If the context does not contain enough information to answer
   the question, respond exactly with:

   NOT_FOUND

4. Give a clear and concise answer.
5. Do not include information that is not supported by the context.
6. You may combine information from multiple provided sources
   when necessary.

DOCUMENT CONTEXT:

{context}

USER QUESTION:

{question}

ANSWER:
"""


    # -----------------------------------------------------
    # 8. Send prompt to LLM service
    #
    # llm_service:
    # Gemini -> if unavailable -> Groq
    # -----------------------------------------------------

    answer = generate_answer(prompt)


    # -----------------------------------------------------
    # 9. No answer returned
    # -----------------------------------------------------

    if not answer:
        return {
            "answer": (
                "I couldn't find an answer to this question "
                "in the uploaded documents."
            ),
            "sources": []
        }


    cleaned_answer = answer.strip()


    # -----------------------------------------------------
    # 10. LLM says context doesn't contain the answer
    # -----------------------------------------------------

    if cleaned_answer.upper().startswith("NOT_FOUND"):
        return {
            "answer": (
                "I couldn't find an answer to this question "
                "in the uploaded documents."
            ),
            "sources": []
        }


    # -----------------------------------------------------
    # 11. Build sources
    # -----------------------------------------------------

    sources = []

    for result in relevant_results:

        sources.append(
            {
                "file_name": result["file_name"],
                "page_number": result["page_number"],
                "relevant_text": result["content"],
                "distance": result["distance"]
            }
        )


    # -----------------------------------------------------
    # 12. Final response
    # -----------------------------------------------------

    return {
        "answer": cleaned_answer,
        "sources": sources
    }