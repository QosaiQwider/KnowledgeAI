import os
import shutil

from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from database.config import get_db

from database.database_models import (
    KnowledgeBase,
    User,
    Document,
    DocumentChunk,
    Conversation,
    Message
)

from schemas.schemas import KnowledgeBaseCreate
from core.auth import get_current_user


# =========================================================
# ROUTER
# =========================================================

router = APIRouter(
    prefix="/knowledge-bases",
    tags=["Knowledge Bases"]
)


# =========================================================
# UPLOAD DIRECTORY
# =========================================================

UPLOAD_DIR = "uploads"


# =========================================================
# CREATE KNOWLEDGE BASE
# =========================================================

@router.post("/")
def create_knowledge_base(
    data: KnowledgeBaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    name = data.name.strip()

    if not name:
        raise HTTPException(
            status_code=400,
            detail="Knowledge base name cannot be empty"
        )

    knowledge_base = KnowledgeBase(
        name=name,
        user_id=current_user.UserID
    )

    db.add(knowledge_base)
    db.commit()
    db.refresh(knowledge_base)

    return {
        "message": "Knowledge base created successfully",

        # Frontend uses id
        "id": knowledge_base.KB_ID,

        # Keep this for compatibility
        "kb_id": knowledge_base.KB_ID,

        "name": knowledge_base.name,

        "document_count": 0,

        "conversation_count": 0
    }


# =========================================================
# GET USER KNOWLEDGE BASES
# =========================================================

@router.get("/")
def get_knowledge_bases(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    knowledge_bases = (
        db.query(KnowledgeBase)
        .filter(
            KnowledgeBase.user_id == current_user.UserID
        )
        .order_by(
            KnowledgeBase.KB_ID.desc()
        )
        .all()
    )

    result = []

    for kb in knowledge_bases:

        # ---------------------------------------------
        # Count documents
        # ---------------------------------------------

        document_count = (
            db.query(Document)
            .filter(
                Document.KB_ID == kb.KB_ID
            )
            .count()
        )

        # ---------------------------------------------
        # Count conversations
        # ---------------------------------------------

        conversation_count = (
            db.query(Conversation)
            .filter(
                Conversation.KB_ID == kb.KB_ID
            )
            .count()
        )

        # ---------------------------------------------
        # Frontend-friendly response
        # ---------------------------------------------

        result.append(
            {
                "id": kb.KB_ID,
                "kb_id": kb.KB_ID,
                "name": kb.name,
                "document_count": document_count,
                "conversation_count": conversation_count
            }
        )

    return result


# =========================================================
# GET ONE KNOWLEDGE BASE
# =========================================================

@router.get("/{kb_id}")
def get_knowledge_base(
    kb_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

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

    document_count = (
        db.query(Document)
        .filter(
            Document.KB_ID == kb_id
        )
        .count()
    )

    conversation_count = (
        db.query(Conversation)
        .filter(
            Conversation.KB_ID == kb_id
        )
        .count()
    )

    return {
        "id": knowledge_base.KB_ID,
        "kb_id": knowledge_base.KB_ID,
        "name": knowledge_base.name,
        "document_count": document_count,
        "conversation_count": conversation_count
    }


# =========================================================
# DELETE KNOWLEDGE BASE
# =========================================================

@router.delete("/{kb_id}")
def delete_knowledge_base(
    kb_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # ---------------------------------------------
    # Verify ownership
    # ---------------------------------------------

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
    # DELETE DATABASE DATA
    # =====================================================

    try:

        # -------------------------------------------------
        # 1. Find documents
        # -------------------------------------------------

        documents = (
            db.query(Document)
            .filter(
                Document.KB_ID == kb_id
            )
            .all()
        )

        document_ids = [
            document.Document_ID
            for document in documents
        ]

        # -------------------------------------------------
        # 2. Delete chunks
        # -------------------------------------------------

        if document_ids:

            (
                db.query(DocumentChunk)
                .filter(
                    DocumentChunk.document_id.in_(
                        document_ids
                    )
                )
                .delete(
                    synchronize_session=False
                )
            )

        # -------------------------------------------------
        # 3. Delete documents
        # -------------------------------------------------

        (
            db.query(Document)
            .filter(
                Document.KB_ID == kb_id
            )
            .delete(
                synchronize_session=False
            )
        )

        # -------------------------------------------------
        # 4. Find conversations
        # -------------------------------------------------

        conversations = (
            db.query(Conversation)
            .filter(
                Conversation.KB_ID == kb_id
            )
            .all()
        )

        conversation_ids = [
            conversation.Conversation_ID
            for conversation in conversations
        ]

        # -------------------------------------------------
        # 5. Delete messages
        # -------------------------------------------------

        if conversation_ids:

            (
                db.query(Message)
                .filter(
                    Message.conversation_id.in_(
                        conversation_ids
                    )
                )
                .delete(
                    synchronize_session=False
                )
            )

        # -------------------------------------------------
        # 6. Delete conversations
        # -------------------------------------------------

        (
            db.query(Conversation)
            .filter(
                Conversation.KB_ID == kb_id
            )
            .delete(
                synchronize_session=False
            )
        )

        # -------------------------------------------------
        # 7. Delete Knowledge Base
        # -------------------------------------------------

        db.delete(knowledge_base)

        # -------------------------------------------------
        # 8. Commit
        # -------------------------------------------------

        db.commit()

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete knowledge base: {str(e)}"
        )

    # =====================================================
    # DELETE UPLOADED FILES FROM DISK
    # =====================================================

    kb_folder = os.path.join(
        UPLOAD_DIR,
        str(kb_id)
    )

    if os.path.exists(kb_folder):

        try:

            shutil.rmtree(
                kb_folder
            )

        except OSError as e:

            print(
                f"Warning: failed to delete folder "
                f"{kb_folder}: {e}"
            )

    # =====================================================
    # RESPONSE
    # =====================================================

    return {
        "message": "Knowledge base deleted successfully",
        "id": kb_id
    }