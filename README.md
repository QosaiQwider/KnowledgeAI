# KnowledgeAI

KnowledgeAI is a full-stack Retrieval-Augmented Generation (RAG) application that allows users to upload documents, organize them into separate knowledge bases, and ask questions based on the content of those documents.

The system retrieves relevant information from uploaded documents and uses an LLM to generate grounded answers. If the answer cannot be found in the uploaded documents, the system informs the user instead of answering from general model knowledge.

## Features

- User registration and login
- JWT-based authentication
- Create and delete knowledge bases
- Upload and manage documents
- Support for PDF, DOCX, and PPTX files
- Automatic document text extraction and chunking
- Text embeddings using Sentence Transformers
- Vector similarity search using PostgreSQL and pgvector
- Retrieval-Augmented Generation (RAG)
- Google Gemini integration
- Groq fallback when Gemini models are unavailable
- Source attribution with document name and page number
- Conversation creation and history
- React-based user interface
- FastAPI REST API

## Tech Stack

### Backend

- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- pgvector
- Sentence Transformers
- Google Gemini API
- Groq API
- JWT Authentication

### Frontend

- React
- Vite
- JavaScript
- React Router
- Lucide React

## Project Structure

```text
KnowledgeAI/
├── backend/
│   ├── core/
│   ├── database/
│   ├── routers/
│   ├── schemas/
│   ├── services/
│   ├── uploads/
│   ├── main.py
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── src/
│   ├── package.json
│   └── ...
│
├── .gitignore
└── README.md
```

## How the RAG Pipeline Works

```text
Uploaded Document
       ↓
Text Extraction
       ↓
Text Chunking
       ↓
Sentence Transformer
       ↓
384-Dimensional Embeddings
       ↓
PostgreSQL + pgvector
       ↓
Vector Similarity Search
       ↓
Relevant Document Chunks
       ↓
Question + Retrieved Context
       ↓
Gemini / Groq
       ↓
Grounded Answer + Sources
```

The application uses the `sentence-transformers/all-MiniLM-L6-v2` model to generate 384-dimensional embeddings.

When a user asks a question, the question is converted into an embedding and compared with stored document chunk embeddings using vector similarity search.

Only sufficiently relevant chunks are provided to the language model as context.

The language model is instructed to answer using only the retrieved document context. If the context does not contain enough information, the application returns a message indicating that an answer could not be found in the uploaded documents.

## Backend Setup

### 1. Create a virtual environment

```bash
python -m venv myenv
```

On Windows:

```bash
myenv\Scripts\activate
```

### 2. Install dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file inside the `backend` directory.

Use `.env.example` as a template.

Required environment variables include:

```env
DATABASE_URL=your_postgresql_connection_string
SECRET_KEY=your_secret_key
GEMINI_API_KEY=your_gemini_api_key
GROQ_API_KEY=your_groq_api_key
```

Do not commit the real `.env` file or API keys to GitHub.

### 4. Configure PostgreSQL

Create the PostgreSQL database used by the application.

Enable the pgvector extension:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### 5. Run the backend

From the `backend` directory:

```bash
uvicorn main:app --reload
```

The backend runs by default at:

```text
http://127.0.0.1:8000
```

FastAPI Swagger documentation is available at:

```text
http://127.0.0.1:8000/docs
```

## Frontend Setup

Open another terminal and navigate to the frontend:

```bash
cd frontend
```

Install the dependencies:

```bash
npm install
```

Start the Vite development server:

```bash
npm run dev
```

The frontend normally runs at:

```text
http://localhost:5173
```

## LLM Fallback

KnowledgeAI first attempts to generate an answer using the configured Gemini models.

If the Gemini models are temporarily unavailable, the application can use Groq as a fallback provider.

```text
Gemini
   ↓ unavailable
Groq
```

This helps improve the availability of the question-answering system when one provider is temporarily unavailable.

## Grounded Question Answering

KnowledgeAI is designed to avoid answering document questions using unsupported general knowledge.

For example:

**Question:**

```text
What are the six levels of Bloom's Revised Taxonomy?
```

If the information exists in an uploaded document, the system returns the answer together with its document source and page number.

If a question is unrelated to the uploaded documents, the system returns:

```text
I couldn't find an answer to this question in the uploaded documents.
```

## Security

- Passwords are stored as hashes rather than plain text.
- Protected API endpoints use JWT authentication.
- API keys and database credentials are stored in environment variables.
- `.env` files are excluded from version control.

## Future Improvements

Possible future improvements include:

- Streaming LLM responses
- More advanced document parsing
- Hybrid semantic and keyword search
- Reranking retrieved chunks
- Improved source highlighting
- Additional document formats
- Deployment using Docker
- Cloud database and storage integration

## Author

**Qosai Qwaider**

Artificial Intelligence Engineering