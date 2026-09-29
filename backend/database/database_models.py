from sqlalchemy import (
    BigInteger,
    Column,
    Integer,
    String,
    Text,
    ForeignKey
)

from sqlalchemy.orm import declarative_base, relationship
from pgvector.sqlalchemy import Vector

# =========================================================
# BASE
# =========================================================

Base = declarative_base()


# =========================================================
# USERS
# DB:
# UserID | FirstName | LastName | Email | password_hash
# =========================================================

class User(Base):
    __tablename__ = "users"

    UserID = Column(
        "UserID",
        Integer,
        primary_key=True
    )

    FirstName = Column(
        "FirstName",
        String(100),
        nullable=False
    )

    LastName = Column(
        "LastName",
        String(100),
        nullable=False
    )

    Email = Column(
        "Email",
        String(255),
        unique=True,
        nullable=False
    )

    password_hash = Column(
        "password_hash",
        Text,
        nullable=False
    )

    knowledge_bases = relationship(
        "KnowledgeBase",
        back_populates="user"
    )


# =========================================================
# KNOWLEDGE BASES
# DB:
# KB-ID | user_id | name
# =========================================================

class KnowledgeBase(Base):
    __tablename__ = "knowledge_bases"

    KB_ID = Column(
        "KB-ID",
        Integer,
        primary_key=True
    )

    user_id = Column(
        "user_id",
        Integer,
        ForeignKey(
            "users.UserID",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    name = Column(
        "name",
        String(255),
        nullable=False
    )

    user = relationship(
        "User",
        back_populates="knowledge_bases"
    )

    documents = relationship(
        "Document",
        back_populates="knowledge_base"
    )

    conversations = relationship(
        "Conversation",
        back_populates="knowledge_base"
    )


# =========================================================
# DOCUMENTS
# DB:
# Document-ID | KB-ID | file_name | file_type | file_size | status
# =========================================================

class Document(Base):
    __tablename__ = "documents"

    Document_ID = Column(
        "Document-ID",
        Integer,
        primary_key=True
    )

    KB_ID = Column(
        "KB-ID",
        Integer,
        ForeignKey(
            "knowledge_bases.KB-ID",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    file_name = Column(
        "file_name",
        String(255),
        nullable=False
    )

    file_type = Column(
        "file_type",
        String(20),
        nullable=False
    )

    file_size = Column(
        "file_size",
        BigInteger
    )

    status = Column(
        "status",
        String(20),
        default="processing"
    )

    knowledge_base = relationship(
        "KnowledgeBase",
        back_populates="documents"
    )

    chunks = relationship(
    "DocumentChunk",
    back_populates="document",
    cascade="all, delete-orphan",
    passive_deletes=True
)


# =========================================================
# DOCUMENT CHUNKS
# DB:
# document-chunks-ID | document_id | content
# page_number | chunk_index
# =========================================================

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    DocumentChunk_ID = Column(
        "document-chunks-ID",
        Integer,
        primary_key=True
    )

    document_id = Column(
        "document_id",
        Integer,
        ForeignKey(
            "documents.Document-ID",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    content = Column(
        "content",
        Text,
        nullable=False
    )

    page_number = Column(
        "page_number",
        Integer
    )

    chunk_index = Column(
        "chunk_index",
        Integer,
        nullable=False
    )

    document = relationship(
        "Document",
        back_populates="chunks"
    )

    embedding = Column(
        Vector(384),
        nullable=True
    )


# =========================================================
# CONVERSATIONS
# DB:
# Conversations-ID | KB-id | title
# =========================================================

class Conversation(Base):
    __tablename__ = "conversations"

    Conversation_ID = Column(
        "Conversations-ID",
        Integer,
        primary_key=True
    )

    KB_ID = Column(
        "KB-id",
        Integer,
        ForeignKey(
            "knowledge_bases.KB-ID",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    title = Column(
        "title",
        String(255)
    )

    knowledge_base = relationship(
        "KnowledgeBase",
        back_populates="conversations"
    )

    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
        passive_deletes=True
)


# =========================================================
# MESSAGES
# DB:
# Messages-ID | Conversation_id | role | content
# =========================================================

class Message(Base):
    __tablename__ = "messages"

    Message_ID = Column(
        "Messages-ID",
        Integer,
        primary_key=True
    )

    conversation_id = Column(
        "Conversation_id",
        Integer,
        ForeignKey(
            "conversations.Conversations-ID",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    role = Column(
        "role",
        String(20),
        nullable=False
    )

    content = Column(
        "content",
        Text,
        nullable=False
    )

    conversation = relationship(
        "Conversation",
        back_populates="messages"
    )