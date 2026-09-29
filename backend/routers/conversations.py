from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database.config import get_db
from database.database_models import (
    Conversation,
    KnowledgeBase,
    Message,
    User
)
from core.auth import get_current_user
from services.rag_service import ask_rag


# =========================================================
# ROUTER
# =========================================================

router = APIRouter(
    tags=["Conversations"]
)


# =========================================================
# REQUEST SCHEMA
# =========================================================

class MessageRequest(BaseModel):
    content: str


# =========================================================
# GET CONVERSATIONS FOR KNOWLEDGE BASE
# =========================================================

@router.get("/knowledge-bases/{kb_id}/conversations")
def get_conversations(
    kb_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # نتأكد إن الـ Knowledge Base للمستخدم الحالي
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

    conversations = (
        db.query(Conversation)
        .filter(
            Conversation.KB_ID == kb_id
        )
        .order_by(
            Conversation.Conversation_ID.desc()
        )
        .all()
    )

    return [
        {
            "id": conversation.Conversation_ID,
            "title": conversation.title,
            "kb_id": conversation.KB_ID
        }
        for conversation in conversations
    ]


# =========================================================
# CREATE CONVERSATION
# =========================================================

@router.post("/knowledge-bases/{kb_id}/conversations")
def create_conversation(
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

    conversation = Conversation(
        KB_ID=kb_id,
        title="New Conversation"
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return {
        "message": "Conversation created successfully",
        "id": conversation.Conversation_ID,
        "title": conversation.title,
        "kb_id": conversation.KB_ID
    }


# =========================================================
# GET CONVERSATION MESSAGES
# =========================================================

@router.get("/conversations/{conversation_id}/messages")
def get_messages(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # نتأكد إن المحادثة موجودة وبتخص Knowledge Base للمستخدم
    conversation = (
        db.query(Conversation)
        .join(
            KnowledgeBase,
            Conversation.KB_ID == KnowledgeBase.KB_ID
        )
        .filter(
            Conversation.Conversation_ID == conversation_id,
            KnowledgeBase.user_id == current_user.UserID
        )
        .first()
    )

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )

    messages = (
        db.query(Message)
        .filter(
            Message.conversation_id == conversation_id
        )
        .order_by(
            Message.Message_ID.asc()
        )
        .all()
    )

    return [
        {
            "id": message.Message_ID,
            "role": message.role,
            "content": message.content
        }
        for message in messages
    ]


# =========================================================
# SEND MESSAGE
# =========================================================

@router.post("/conversations/{conversation_id}/messages")
def send_message(
    conversation_id: int,
    data: MessageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # -----------------------------------------------------
    # 1. Validate message
    # -----------------------------------------------------

    question = data.content.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty"
        )


    # -----------------------------------------------------
    # 2. Get conversation and verify ownership
    # -----------------------------------------------------

    conversation = (
        db.query(Conversation)
        .join(
            KnowledgeBase,
            Conversation.KB_ID == KnowledgeBase.KB_ID
        )
        .filter(
            Conversation.Conversation_ID == conversation_id,
            KnowledgeBase.user_id == current_user.UserID
        )
        .first()
    )

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )


    # -----------------------------------------------------
    # 3. Save user message
    # -----------------------------------------------------

    user_message = Message(
        conversation_id=conversation_id,
        role="user",
        content=question
    )

    db.add(user_message)
    db.commit()
    db.refresh(user_message)


    # -----------------------------------------------------
    # 4. Ask RAG
    # -----------------------------------------------------

    try:

        rag_result = ask_rag(
            db=db,
            kb_id=conversation.KB_ID,
            question=question
        )

    except Exception as e:

        print(
            f"RAG ERROR: {type(e).__name__}: {e}"
        )

        raise HTTPException(
            status_code=503,
            detail=(
                "The AI service is temporarily unavailable. "
                "Please try again."
            )
        )


    answer = rag_result["answer"]
    sources = rag_result["sources"]


    # -----------------------------------------------------
    # 5. Save assistant message
    # -----------------------------------------------------

    assistant_message = Message(
        conversation_id=conversation_id,
        role="assistant",
        content=answer
    )

    db.add(assistant_message)


    # -----------------------------------------------------
    # 6. Automatically name new conversation
    # -----------------------------------------------------

    if (
        not conversation.title
        or conversation.title == "New Conversation"
    ):

        # أول سؤال بصير عنوان المحادثة
        conversation.title = (
            question[:60]
            if len(question) <= 60
            else question[:57] + "..."
        )


    db.commit()
    db.refresh(assistant_message)


    # -----------------------------------------------------
    # 7. Return answer + sources
    # -----------------------------------------------------

    return {
        "user_message": {
            "id": user_message.Message_ID,
            "role": "user",
            "content": user_message.content
        },

        "assistant_message": {
            "id": assistant_message.Message_ID,
            "role": "assistant",
            "content": assistant_message.content
        },

        "answer": answer,

        "sources": sources
    }


# =========================================================
# DELETE CONVERSATION
# =========================================================

@router.delete("/conversations/{conversation_id}")
def delete_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    conversation = (
        db.query(Conversation)
        .join(
            KnowledgeBase,
            Conversation.KB_ID == KnowledgeBase.KB_ID
        )
        .filter(
            Conversation.Conversation_ID == conversation_id,
            KnowledgeBase.user_id == current_user.UserID
        )
        .first()
    )

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )

    db.delete(conversation)
    db.commit()

    return {
        "message": "Conversation deleted successfully"
    }