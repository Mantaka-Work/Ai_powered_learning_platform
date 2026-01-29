# AI-Powered Supplementary Learning Platform - Copilot Instructions

## Project Overview
Hackathon project building an AI-powered university course learning platform with 5 core parts:
1. **CMS** - Content management for Theory/Lab materials
2. **Search** - RAG-based semantic search + Perplexity web search fallback
3. **Generation** - AI-generated notes, summaries, and code examples
4. **Validation** - Syntax checking, grounding validation, source credibility
5. **Chat** - Conversational interface integrating all features

## Architecture

### Tech Stack
- **Backend**: FastAPI (Python 3.10+) + LangChain/LlamaIndex
- **Frontend**: Next.js 14 + shadcn/ui + Tailwind CSS
- **Database**: Supabase (PostgreSQL + pgvector for embeddings + Storage)
- **AI**: OpenAI GPT-4o-mini (chat), text-embedding-3-small (embeddings)
- **Web Search**: Perplexity API (fallback when course relevance <40%)

### Key Data Flow
```
Upload → Parse → Chunk → Embed → Store in pgvector
Query → Embed → Vector search → (if relevance <40%) Perplexity → LLM → Response
```

## Directory Structure Conventions

### Backend (`backend/`)
- `app/api/routes/` - FastAPI route handlers (materials, search, generate, chat, validate)
- `app/core/rag/` - Embedding pipeline, vectorstore, retriever, chains
- `app/core/generation/` - Theory/code generators with prompts
- `app/core/validation/` - Code syntax & content grounding validators
- `app/core/mcp/` - Perplexity client for web search integration
- `app/db/repositories/` - Supabase data access layer
- `app/services/` - Business logic orchestration

### Frontend (`frontend/`)
- `app/(dashboard)/courses/[courseId]/` - Course-specific pages (materials, search, generate, chat)
- `components/Chat/` - Chat UI with `WebSearchBadge` for external sources
- `components/Search/` - Hybrid search with `WebSearchResults` section
- `hooks/` - `useChat`, `useSearch`, `useWebSearch`, `useGeneration`
- `lib/api.ts` - Backend API client

## Critical Patterns

### Hybrid Search (Course + Web)
```python
# Auto-trigger web search when relevance < 40%
async def search_hybrid(query, course_id, include_web=None):
    course_results = await vectorstore.search(query)
    if include_web is None:
        include_web = calculate_relevance(course_results) < 0.40
    if include_web:
        web_results = await perplexity_service.search(query)
        return combine_results(course_results, web_results)
    return course_results
```

### Content Generation with Source Attribution
Always track and display whether content comes from course materials or web search:
```python
return {
    "content": generated,
    "sources": {"course": course_sources, "web": web_sources},
    "source_mix_ratio": 0.7  # 70% course, 30% web
}
```

### Validation Requirements
- **Code**: Syntax check → Lint → Static analysis → (optional) sandboxed execution
- **Theory**: Grounding check (cites sources?) → Structure check → Relevance score
- **Web sources**: Check domain credibility, recency, proper citation with URLs

## API Endpoint Patterns
- `POST /search/semantic` - Course materials only
- `POST /search/hybrid` - Course + conditional web search
- `POST /search/web` - Force Perplexity web search
- `POST /generate/theory` - Notes/summaries with `use_web` flag
- `POST /generate/code` - Code examples with language param
- `POST /chat/message` - Streaming responses with `include_web_search` option

## Environment Variables Required
```bash
OPENAI_API_KEY, OPENAI_CHAT_MODEL=gpt-4o-mini, OPENAI_EMBEDDING_MODEL=text-embedding-3-small
SUPABASE_URL, SUPABASE_KEY, SUPABASE_SERVICE_KEY
PERPLEXITY_API_KEY, PERPLEXITY_RATE_LIMIT=5
```

## Perplexity Integration Rules
- **Cache results** for 7 days to stay within free tier (100 searches/month)
- **Only trigger** when relevance <40% OR user explicitly requests web search
- **Always label** web results clearly: "🌐 From Web" vs "📚 From Course"
- **Rate limit**: 5 searches/minute on free tier

## Performance Targets
- Search (materials): <2s | Search (with web): <4s
- Generation: 30-60s (45-90s with web context)
- Chat streaming: start within 5s

## File Upload Support
PDF, PPTX, DOCX, code files (.py, .js, .java, .cpp), Markdown, text (max 50MB)

## Validation Display Pattern
- ✅ Validated (ready to use)
- ⚠️ Warn (usable with issues)  
- ❌ Failed (regenerate needed)
