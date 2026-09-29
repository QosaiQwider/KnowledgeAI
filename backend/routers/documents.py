import os
import shutil

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile
)

from sqlalchemy.orm import Session

from database.config import get_db

from database.database_models import (
    Document,
    KnowledgeBase,
    User,
    DocumentChunk
)

from services.document_processor import extract_text, chunk_text
from services.embedding_service import generate_embedding
from core.auth import get_current_user


# =========================================================
# ROUTER
# =========================================================

router = APIRouter(
    tags=["Documents"]
)


# =========================================================
# UPLOAD FOLDER
# =========================================================

UPLOAD_DIR = "uploads"

os.makedirs(
    UPLOAD_DIR,
    exist_ok=True
)


# =========================================================
# GET DOCUMENTS
# =========================================================

@router.get("/knowledge-bases/{kb_id}/documents")
def get_documents(
    kb_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # -----------------------------------------------------
    # Check that Knowledge Base exists
    # and belongs to current user
    # -----------------------------------------------------

    knowledge_base = (
        db.query(KnowledgeBase)
        .filter(
            KnowledgeBase.KB_ID == kb_id,
            KnowledgeBase.user_id == current_user.UserID
        )
        .first()
    )

    if not knowledge_base:
        raise HTTPException(
            status_code=404,
            detail="Knowledge base not found"
        )


    # -----------------------------------------------------
    # Get documents
    # -----------------------------------------------------

    documents = (
        db.query(Document)
        .filter(
            Document.KB_ID == kb_id
        )
        .all()
    )


    return [
        {
            "id": document.Document_ID,
            "file_name": document.file_name,
            "file_type": document.file_type,
            "file_size": document.file_size,
            "status": document.status
        }
        for document in documents
    ]


# =========================================================
# UPLOAD + PROCESS DOCUMENTS
# =========================================================

@router.post("/knowledge-bases/{kb_id}/documents")
def upload_documents(
    kb_id: int,
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # =====================================================
    # 1. CHECK KNOWLEDGE BASE
    # =====================================================

    knowledge_base = (
        db.query(KnowledgeBase)
        .filter(
            KnowledgeBase.KB_ID == kb_id,
            KnowledgeBase.user_id == current_user.UserID
        )
        .first()
    )

    if not knowledge_base:
        raise HTTPException(
            status_code=404,
            detail="Knowledge base not found"
        )


    # =====================================================
    # 2. ALLOWED FILE TYPES
    # =====================================================

    allowed_extensions = {
        ".pdf",
        ".docx",
        ".pptx",
        ".txt"
    }


    # =====================================================
    # 3. CREATE KNOWLEDGE BASE FOLDER
    # =====================================================

    kb_folder = os.path.join(
        UPLOAD_DIR,
        str(kb_id)
    )

    os.makedirs(
        kb_folder,
        exist_ok=True
    )


    uploaded_documents = []


    # =====================================================
    # 4. PROCESS EACH FILE
    # =====================================================

    for file in files:

        if not file.filename:
            continue


        # -------------------------------------------------
        # Get extension
        # -------------------------------------------------

        extension = os.path.splitext(
            file.filename
        )[1].lower()


        if extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file.filename}"
            )


        file_type = extension.replace(".", "")


        # -------------------------------------------------
        # File path
        # -------------------------------------------------

        file_path = os.path.join(
            kb_folder,
            file.filename
        )


        # =================================================
        # 5. SAVE FILE
        # =================================================

        try:

            with open(file_path, "wb") as buffer:

                shutil.copyfileobj(
                    file.file,
                    buffer
                )

        except Exception as e:

            raise HTTPException(
                status_code=500,
                detail=f"Failed to save file: {str(e)}"
            )


        # =================================================
        # 6. GET FILE SIZE
        # =================================================

        file_size = os.path.getsize(
            file_path
        )


        # =================================================
        # 7. CREATE DOCUMENT RECORD
        # =================================================

        document = Document(
            KB_ID=kb_id,
            file_name=file.filename,
            file_type=file_type,
            file_size=file_size,
            status="processing"
        )

        db.add(document)

        # Generate Document_ID before final commit
        db.flush()


        # =================================================
        # 8. EXTRACT TEXT
        #    +
        #    CHUNKING
        #    +
        #    EMBEDDINGS
        # =================================================

        try:

            # ---------------------------------------------
            # Extract text from document
            # ---------------------------------------------

            pages = extract_text(
                file_path,
                file_type
            )


            chunk_index = 0


            # ---------------------------------------------
            # Process every page
            # ---------------------------------------------

            for page in pages:

                text = page.get(
                    "text",
                    ""
                )


                if not text.strip():
                    continue


                # =========================================
                # CHUNK TEXT
                # =========================================

                chunks = chunk_text(
                    text,
                    chunk_size=1000,
                    overlap=200
                )


                # =========================================
                # PROCESS EACH CHUNK
                # =========================================

                for chunk in chunks:

                    # -------------------------------------
                    # Generate embedding
                    #
                    # all-MiniLM-L6-v2
                    # output = 384 dimensions
                    # -------------------------------------

                    embedding = generate_embedding(
                        chunk
                    )


                    # -------------------------------------
                    # Create chunk database record
                    # -------------------------------------

                    document_chunk = DocumentChunk(

                        document_id=document.Document_ID,

                        content=chunk,

                        page_number=page.get(
                            "page_number"
                        ),

                        chunk_index=chunk_index,

                        embedding=embedding
                    )


                    db.add(
                        document_chunk
                    )


                    chunk_index += 1


            # =================================================
            # 9. CHECK THAT CHUNKS WERE CREATED
            # =================================================

            if chunk_index == 0:

                document.status = "failed"

                db.commit()

                raise HTTPException(
                    status_code=400,
                    detail=f"No readable text found in {file.filename}"
                )


            # =================================================
            # 10. DOCUMENT READY
            # =================================================

            document.status = "ready"

            db.commit()

            db.refresh(
                document
            )


        except HTTPException:

            raise


        except Exception as e:

            db.rollback()

            raise HTTPException(
                status_code=500,
                detail=f"Failed to process {file.filename}: {str(e)}"
            )


        # =================================================
        # 11. RESPONSE DATA
        # =================================================

        uploaded_documents.append(
            {
                "id": document.Document_ID,
                "file_name": document.file_name,
                "file_type": document.file_type,
                "file_size": document.file_size,
                "status": document.status,
                "chunks_created": chunk_index
            }
        )


    # =====================================================
    # FINAL RESPONSE
    # =====================================================

    return {
        "message": "Documents uploaded, chunked and embedded successfully",
        "documents": uploaded_documents
    }


# =========================================================
# DELETE DOCUMENT
# =========================================================

@router.delete("/documents/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # =====================================================
    # CHECK DOCUMENT OWNERSHIP
    # =====================================================

    document = (
        db.query(Document)
        .join(
            KnowledgeBase,
            Document.KB_ID == KnowledgeBase.KB_ID
        )
        .filter(
            Document.Document_ID == document_id,
            KnowledgeBase.user_id == current_user.UserID
        )
        .first()
    )


    if not document:

        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )


    # =====================================================
    # FILE PATH
    # =====================================================

    file_path = os.path.join(
        UPLOAD_DIR,
        str(document.KB_ID),
        document.file_name
    )


    # =====================================================
    # DELETE DATABASE RECORD
    # =====================================================

    db.delete(
        document
    )

    db.commit()


    # =====================================================
    # DELETE FILE FROM DISK
    # =====================================================

    if os.path.exists(
        file_path
    ):

        try:

            os.remove(
                file_path
            )

        except OSError:

            pass


    return {
        "message": "Document deleted successfully"
    }