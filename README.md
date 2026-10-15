# RAG Citation Agent

A Retrieval-Augmented Generation (RAG) application that answers questions using uploaded documents and provides evidence-backed responses with citation validation and claim verification.

## Overview

RAG Citation Agent combines semantic document retrieval with large language models to generate answers grounded in document content. It is designed to make answers easier to inspect by exposing the supporting evidence and verification results.

### Key Features

- **Document ingestion:** Upload documents for processing.
- **Semantic retrieval:** Retrieve relevant document chunks using embeddings and FAISS.
- **Grounded answers:** Generate responses from retrieved evidence.
- **Citation validation:** Validate cited evidence identifiers.
- **Claim verification:** Check generated claims against retrieved evidence.
- **Provider selection:** Use Groq or a local Ollama model.
- **Persistent storage:** Store document metadata and application records in SQLite.
- **Performance logging:** Record model request timing and token usage.
- **React dashboard:** Interact with the application through a React and TypeScript frontend.
- **Automated tests:** Test retrieval, citations, claim verification, ingestion, and provider behavior.

## Architecture

```text
React + TypeScript Frontend
          |
          v
       FastAPI
          |
          v
    Answer Service
       /      \
      v        v
Document      LLM Provider
Retrieval     /          \
   |        Groq         Ollama
   v
 FAISS Index
   |
   v
Retrieved Evidence
   |
   v
Answer + Citations + Claim Verification
```

## Technology Stack

| Component | Technology |
|---|---|
| Frontend | React, TypeScript, Vite |
| Backend API | FastAPI |
| Data validation | Pydantic |
| Embeddings | Sentence Transformers |
| Vector search | FAISS |
| Database | SQLite |
| LLM providers | Groq API, Ollama |
| Testing | Pytest |

## Requirements

- Python 3.12 recommended
- Node.js and npm
- Git
- A Groq API key for hosted inference, or Ollama installed locally for local inference

## Installation

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd RAG-Citation-Agent
```

Replace `YOUR_GITHUB_REPOSITORY_URL` with the actual repository URL after publishing.

### 2. Create a Python virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install backend dependencies

```powershell
python -m pip install -r requirements.txt
python -m pip install groq python-dotenv
```

### 4. Configure environment variables

Copy `.env.example` to `.env` in the project root and configure your local values:

```dotenv
GROQ_API_KEY=
GROQ_MODEL=openai/gpt-oss-20b
LLM_PROVIDER=groq
```

Add your own Groq API key locally. Never commit `.env` or publish API keys.

To use Ollama instead, set:

```dotenv
LLM_PROVIDER=ollama
```

Ensure the selected Ollama model is installed and the Ollama service is running.

### 5. Start the backend

From the project root:

```powershell
cd backend
python -m uvicorn app.main:app --reload
```

API base URL: `http://127.0.0.1:8000`

Interactive API documentation: `http://127.0.0.1:8000/docs`

### 6. Start the frontend

Open a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite, normally `http://localhost:5173`.

## Testing

From the `backend` directory:

```powershell
python -m pytest tests -q
```

The project has previously passed **43 automated tests**.

Build the frontend production bundle:

```powershell
cd frontend
npm run build
```

The production build has also completed successfully.

## Performance

During local testing with the Groq `openai/gpt-oss-20b` model, one successful request reported:

| Operation | Reported time |
|---|---:|
| Initial answer generation | 2.30 seconds |
| Batch claim verification | 1.19 seconds |
| Combined model time | 3.49 seconds |

These are measurements from one request, not guaranteed benchmarks. Total HTTP response time can be higher because it also includes retrieval and application processing.

## API Endpoints

The application includes routes for:

- `/api/health` — health check
- `/api/documents/upload` — document upload
- `/api/documents/` — document listing
- `/api/search/` — evidence retrieval
- `/api/answers/` — answer generation

See `/docs` for the routes and request schemas exposed by the running backend.

## Security Notes

- Keep API keys in `.env`, never in source code.
- Keep `.env` excluded from Git.
- Do not publish private documents, local databases, or generated indexes.
- Use `.env.example` only for non-secret configuration placeholders.
- Review files before every commit.

## Current Status

- Groq provider integration completed and tested with a successful API request.
- Ollama provider retained as an alternative.
- Citation validation and claim verification enabled.
- Backend test suite: 43 tests passed in the latest recorded run.
- Frontend production build: successful in the latest recorded run.

## Future Improvements

- Add authentication and user-specific document access.
- Add automated end-to-end tests.
- Add deployment configuration and hosted demo.
- Add monitoring and structured application logs.
- Expand evaluation datasets for retrieval quality and factual grounding.

## License

Choose a license before public distribution. Until one is added, no explicit open-source license is granted.
