# KnowledgeAI — React Frontend

Functional React/Vite frontend for the AI Knowledge Base & RAG platform.

## Included
- Register / Login / Logout
- Protected routes with bearer token
- Dashboard
- Knowledge Base create/list/delete
- Knowledge Base detail
- Multi-file upload: PDF, DOCX, PPTX, TXT
- Document list, processing/ready/failed status, delete
- Conversation history
- Create/open chat
- Chat messages, loading/error states
- Source display (document, page/section, relevant content)
- Responsive minimal UI

## Run
```bash
npm install
cp .env.example .env
npm run dev
```
Windows PowerShell:
```powershell
Copy-Item .env.example .env
npm run dev
```

## Backend URL
`.env`:
```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

## Expected API contract
The frontend currently expects:
- POST `/register`
- POST `/login` -> `{ "access_token": "..." }` or `{ "token": "..." }`
- GET/POST `/knowledge-bases`
- DELETE `/knowledge-bases/{id}`
- GET/POST `/knowledge-bases/{id}/documents`
- DELETE `/documents/{id}`
- GET/POST `/knowledge-bases/{id}/conversations`
- GET/POST `/conversations/{id}/messages`

If your FastAPI paths or JSON field names differ, edit only `src/services/api.js` in most cases.

## Important
This frontend does not implement RAG itself. It calls the backend. The backend is responsible for authentication, document processing, embeddings/pgvector retrieval, LLM generation, grounded-answer behavior, and source metadata.
