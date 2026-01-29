# AI-Powered Learning Platform Backend

## Quick Start

1. Create a virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and fill in your API keys

4. Run the server:
```bash
uvicorn app.main:app --reload --port 8000
```

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── routes/          # API route handlers
│   │   └── dependencies.py  # Dependency injection
│   ├── core/
│   │   ├── rag/            # RAG pipeline (embeddings, retriever, chains)
│   │   ├── document_processing/  # Parsers, chunking
│   │   ├── generation/     # Theory/code generators
│   │   ├── validation/     # Code/content validators
│   │   └── mcp/           # Perplexity web search
│   ├── db/
│   │   ├── repositories/   # Data access layer
│   │   ├── models.py      # Pydantic models
│   │   └── supabase_client.py
│   ├── services/           # Business logic
│   ├── utils/              # Helpers, logging, validators
│   ├── config.py           # Settings management
│   └── main.py             # FastAPI app
├── requirements.txt
└── .env.example
```

## API Endpoints

- `POST /api/v1/auth/login` - User authentication
- `POST /api/v1/materials/upload` - Upload course materials
- `POST /api/v1/search/semantic` - Search course materials
- `POST /api/v1/search/hybrid` - Search with web fallback
- `POST /api/v1/generate/theory` - Generate notes/summaries
- `POST /api/v1/generate/code` - Generate code examples
- `POST /api/v1/chat/message` - Send chat message
- `POST /api/v1/validate/code` - Validate code
- `GET /api/v1/health` - Health check

## Environment Variables

See `.env.example` for required configuration.
