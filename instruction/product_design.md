# Product Design & Technical Architecture

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           FRONTEND (Next.js)                             │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐   │
│  │   Auth UI    │ │  Materials   │ │  Search UI   │ │  Chat UI     │   │
│  │   Pages      │ │  Browser     │ │  Interface   │ │  Component   │   │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘   │
│         ↓                ↓                ↓                ↓              │
│  ┌────────────────────────────────────────────────────────────────┐     │
│  │              API Client Layer (Axios/Fetch)                    │     │
│  └────────────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↕ HTTP/WebSocket
┌─────────────────────────────────────────────────────────────────────────┐
│                        BACKEND (FastAPI/Python)                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                       API Routes Layer                          │   │
│  │  /materials  /search  /generate  /chat  /validate  /auth       │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│         ↓         ↓        ↓        ↓        ↓         ↓                │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    Services & Business Logic                    │   │
│  │  ┌──────────┐ ┌──────────┐ ┌────────┐ ┌───────┐ ┌────────────┐ │   │
│  │  │Material  │ │Document  │ │Search  │ │Gen.   │ │Validation  │ │   │
│  │  │Service   │ │Process   │ │Service │ │Service│ │Service     │ │   │
│  │  └──────────┘ └──────────┘ └────────┘ └───────┘ └────────────┘ │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│         ↓           ↓            ↓          ↓           ↓               │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │              Core RAG & AI Engine (LangChain/LlamaIndex)        │   │
│  │  ┌──────────┐ ┌──────────┐ ┌────────┐ ┌────────┐ ┌──────────┐ │   │
│  │  │Embedding │ │Chunking  │ │Retriev.│ │Chat    │ │Generation│ │   │
│  │  │Pipeline  │ │Strategy  │ │Logic   │ │Agent   │ │Chains    │ │   │
│  │  └──────────┘ └──────────┘ └────────┘ └────────┘ └──────────┘ │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│         ↓           ↓            ↓          ↓           ↓               │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    Data Access Layer (Repos)                    │   │
│  │  ┌──────────┐ ┌──────────┐ ┌─────────┐ ┌──────────────────┐   │   │
│  │  │Material  │ │Vector    │ │Chat     │ │Generated Content │   │   │
│  │  │Repository│ │Repository│ │Repo     │ │Repository        │   │   │
│  │  └──────────┘ └──────────┘ └─────────┘ └──────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                ↓                    ↓                    ↓
         ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
         │  Supabase    │     │   OpenAI     │     │  Perplexity  │
         │  Database    │     │   API        │     │   API        │
         │  + pgvector  │     │   (GPT-4o)   │     │  (Web Search)│
         │  + Storage   │     │              │     │              │
         └──────────────┘     └──────────────┘     └──────────────┘
```

---

## 🔗 Perplexity Integration (NEW!)

### What is Perplexity in This Context?

**Perplexity API** = Web search + AI synthesis engine that finds current information from the internet

**Usage in Your System:**
- When a student's query isn't well-answered by course materials
- When generating content that needs current/real-world examples
- When student explicitly requests "search the web"
- For trending topics, new technologies, breaking news

### Integration Points

```
1. SEARCH (Part 2)
   User Query → Course Materials Search (low relevance?)
              → Trigger Perplexity Web Search
              → Combine & rank results
              → Display with clear source labels

2. GENERATION (Part 3)
   User Request → Search Course Materials
               → If insufficient → Trigger Perplexity
               → Combine sources
               → Generate content with citations

3. CHAT (Part 5)
   User Question → Search Course Materials
               → Check relevance
               → If low relevance → Offer web search option
               → User can accept/decline
               → Integrate results into conversation
```

### Perplexity API Setup

```python
# backend/app/core/mcp/perplexity_client.py

from perplexity_api import PerplexityClient

class PerplexitySearchService:
    def __init__(self):
        self.client = PerplexityClient(
            api_key=settings.PERPLEXITY_API_KEY
        )
    
    async def search(self, query: str, limit: int = 5):
        """
        Search web via Perplexity
        
        Returns:
        {
            "results": [
                {
                    "title": "Page title",
                    "url": "https://example.com",
                    "snippet": "Relevant excerpt...",
                    "relevance_score": 0.92,
                    "source_domain": "example.com",
                    "published_date": "2026-01-29"
                }
            ],
            "took_ms": 1200
        }
        """
        results = await self.client.search(
            query=query,
            num_results=limit,
            recency="week"  # Recent results (configurable)
        )
        return results
    
    async def research(self, topic: str, context: str = None):
        """
        Deep research on a topic with synthesis
        
        Combines multiple sources + AI synthesis
        Good for generation use cases
        """
        research = await self.client.research(
            topic=topic,
            context=context,
            max_sources=10
        )
        return research
```

### When to Use Perplexity

**✅ USE Perplexity When:**
- Search relevance score < 40% in course materials
- Topic involves recent events (AI news, COVID-19, etc)
- Technology with frequent updates (framework versions, best practices)
- Student explicitly asks "search the web"
- Generating content about current trends

**❌ DON'T USE Perplexity When:**
- Course materials have good answers (>70% relevance)
- Topic is stable/unchanging (history, theory)
- Student explicitly says "only use course materials"
- System is under high load (cost optimization)

### Cost & Rate Limits

```
Perplexity API Pricing:
- Free tier: 100 searches/month
- Pro tier: $20/month = 10K searches
- Enterprise: Custom pricing

For hackathon: FREE TIER is enough (100 searches total)

Rate limits:
- Free: 5 searches per minute
- Pro: 100 searches per minute

Cost optimization:
- Cache search results (don't search same query twice)
- Batch similar searches
- Add cooldown period if rate-limited
```

---

## File Structure (Complete)

### Backend Directory Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                           # FastAPI app, routes registration
│   ├── config.py                         # Settings, env variables
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py                   # POST /auth/login, /auth/register
│   │   │   ├── materials.py              # POST /materials/upload
│   │   │   │                             # GET /materials/{course_id}
│   │   │   │                             # DELETE /materials/{id}
│   │   │   ├── search.py                 # POST /search/semantic
│   │   │   │                             # GET /search/filters
│   │   │   │                             # POST /search/web (NEW - Perplexity)
│   │   │   ├── generate.py               # POST /generate/theory
│   │   │   │                             # POST /generate/code
│   │   │   │                             # GET /generate/{id}/status
│   │   │   ├── chat.py                   # POST /chat/sessions
│   │   │   │                             # POST /chat/message
│   │   │   │                             # GET /chat/sessions/{id}
│   │   │   ├── validation.py             # POST /validate/code
│   │   │   │                             # POST /validate/content
│   │   │   └── health.py                 # GET /health (monitoring)
│   │   └── dependencies.py               # Dependency injection
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   │
│   │   ├── rag/
│   │   │   ├── __init__.py
│   │   │   ├── embeddings.py             # OpenAI embeddings service
│   │   │   ├── vectorstore.py            # Supabase pgvector operations
│   │   │   ├── retriever.py              # RAG retrieval logic
│   │   │   ├── chains.py                 # LangChain chains & prompts
│   │   │   └── memory.py                 # Conversation memory management
│   │   │
│   │   ├── document_processing/
│   │   │   ├── __init__.py
│   │   │   ├── parsers.py                # PDF, PPTX, DOCX parsers
│   │   │   ├── chunking.py               # Text splitting strategies
│   │   │   ├── code_parser.py            # Syntax-aware code analysis
│   │   │   └── metadata_extractor.py     # Extract metadata from files
│   │   │
│   │   ├── generation/
│   │   │   ├── __init__.py
│   │   │   ├── theory_generator.py       # Notes/summary generation
│   │   │   ├── code_generator.py         # Code example generation
│   │   │   ├── prompts.py                # All prompt templates
│   │   │   └── formatters.py             # Output formatting (MD, JSON)
│   │   │
│   │   ├── validation/
│   │   │   ├── __init__.py
│   │   │   ├── code_validator.py         # Syntax, lint, execution
│   │   │   ├── content_validator.py      # Grounding, structure check
│   │   │   └── evaluators.py             # Scoring & scoring logic
│   │   │
│   │   ├── agents/
│   │   │   ├── __init__.py
│   │   │   ├── chat_agent.py             # LangChain agent setup
│   │   │   └── tools.py                  # Agent tool definitions
│   │   │
│   │   └── mcp/
│   │       ├── __init__.py
│   │       ├── perplexity_client.py      # Perplexity web search integration
│   │       └── web_search_service.py     # Web search orchestration (NEW!)
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   ├── supabase_client.py            # Supabase client init
│   │   ├── models.py                     # Pydantic schemas/models
│   │   └── repositories/
│   │       ├── __init__.py
│   │       ├── base_repo.py              # Base repository class
│   │       ├── material_repo.py          # Material CRUD operations
│   │       ├── vector_repo.py            # Vector store operations
│   │       ├── chat_repo.py              # Chat history operations
│   │       ├── generation_repo.py        # Generated content storage
│   │       └── web_search_repo.py        # Web search results cache (NEW!)
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── material_service.py           # Material business logic
│   │   ├── search_service.py             # Search orchestration (hybrid)
│   │   ├── web_search_service.py         # Web search orchestration (NEW!)
│   │   ├── generation_service.py         # Generation orchestration
│   │   ├── chat_service.py               # Chat orchestration
│   │   └── storage_service.py            # Supabase Storage operations
│   │
│   └── utils/
│       ├── __init__.py
│       ├── logger.py                     # Logging setup
│       ├── validators.py                 # Input validation helpers
│       └── helpers.py                    # Utility functions
│
├── tests/
│   ├── __init__.py
│   ├── test_materials.py
│   ├── test_search.py
│   ├── test_generation.py
│   ├── test_chat.py
│   └── test_web_search.py                # Web search tests (NEW!)
│
├── scripts/
│   ├── seed_data.py                      # Load test data
│   └── init_db.py                        # Initialize database
│
├── requirements.txt
├── .env.example
├── .env.local (gitignore)
├── README.md
├── run.sh                                # Start server
└── Dockerfile                            # Container config
```

### Frontend Directory Structure

```
frontend/
├── app/
│   ├── layout.tsx                        # Root layout, navbar, sidebar
│   ├── page.tsx                          # Home page
│   │
│   ├── (auth)/
│   │   ├── login/
│   │   │   └── page.tsx
│   │   ├── register/
│   │   │   └── page.tsx
│   │   └── layout.tsx
│   │
│   ├── (dashboard)/
│   │   ├── layout.tsx                    # Dashboard layout
│   │   │
│   │   ├── courses/
│   │   │   ├── page.tsx                  # Course list
│   │   │   └── [courseId]/
│   │   │       ├── layout.tsx
│   │   │       ├── page.tsx              # Course overview
│   │   │       │
│   │   │       ├── materials/
│   │   │       │   ├── page.tsx          # Browse materials
│   │   │       │   └── [materialId]/
│   │   │       │       └── page.tsx      # Material detail view
│   │   │       │
│   │   │       ├── search/
│   │   │       │   └── page.tsx          # Search interface
│   │   │       │
│   │   │       ├── generate/
│   │   │       │   └── page.tsx          # Generation form
│   │   │       │
│   │   │       └── chat/
│   │   │           └── page.tsx          # Chat interface
│   │   │
│   │   └── admin/
│   │       ├── page.tsx                  # Admin dashboard
│   │       └── upload/
│   │           └── page.tsx              # Bulk upload
│   │
│   └── api/                              # API route handlers (middleware)
│       └── [...].ts
│
├── components/
│   ├── ui/                               # shadcn/ui components (reusable)
│   │   ├── button.tsx
│   │   ├── input.tsx
│   │   ├── card.tsx
│   │   ├── dialog.tsx
│   │   ├── select.tsx
│   │   └── toast.tsx
│   │
│   ├── layout/
│   │   ├── Navbar.tsx
│   │   ├── Sidebar.tsx
│   │   └── Footer.tsx
│   │
│   ├── Chat/
│   │   ├── ChatInterface.tsx             # Main chat component
│   │   ├── MessageList.tsx               # Messages display
│   │   ├── InputBox.tsx                  # Message input
│   │   ├── ChatSession.tsx               # Session management
│   │   ├── SourcePanel.tsx               # Show sources/references
│   │   └── WebSearchBadge.tsx            # Badge for web sources (NEW!)
│   │
│   ├── Materials/
│   │   ├── MaterialBrowser.tsx           # Material list view
│   │   ├── MaterialCard.tsx              # Single material card
│   │   ├── MaterialUpload.tsx            # Upload component
│   │   ├── MaterialMetadata.tsx          # Metadata form
│   │   └── MaterialPreview.tsx           # Preview modal
│   │
│   ├── Search/
│   │   ├── SearchBar.tsx                 # Search input
│   │   ├── SearchResults.tsx             # Results display (hybrid)
│   │   ├── FilterPanel.tsx               # Search filters
│   │   ├── ResultCard.tsx                # Single result card
│   │   └── WebSearchResults.tsx          # Web results section (NEW!)
│   │
│   ├── Generation/
│   │   ├── GenerationForm.tsx            # Request form
│   │   ├── ContentPreview.tsx            # Generated content view
│   │   ├── ValidationBadge.tsx           # Validation status display
│   │   └── ValidationReport.tsx          # Detailed validation report
│   │
│   ├── Admin/
│   │   ├── AdminDashboard.tsx            # Admin overview
│   │   ├── MaterialsManagement.tsx       # Admin material control
│   │   └── AnalyticsDashboard.tsx        # Usage analytics
│   │
│   └── Common/
│       ├── LoadingSpinner.tsx
│       ├── ErrorBoundary.tsx
│       └── NotFound.tsx
│
├── lib/
│   ├── api.ts                            # API client setup & functions
│   ├── supabase.ts                       # Supabase client config
│   ├── perplexity.ts                     # Perplexity client (NEW!)
│   ├── utils.ts                          # Utility functions
│   ├── validators.ts                     # Form validators
│   └── constants.ts                      # App constants
│
├── hooks/
│   ├── useChat.ts                        # Chat logic hook
│   ├── useSearch.ts                      # Search logic hook (now hybrid)
│   ├── useWebSearch.ts                   # Web search hook (NEW!)
│   ├── useMaterials.ts                   # Materials CRUD hook
│   ├── useGeneration.ts                  # Generation hook
│   ├── useAuth.ts                        # Auth state hook
│   └── useSupabase.ts                    # Supabase operations
│
├── types/
│   └── index.ts                          # TypeScript interfaces
│
├── styles/
│   └── globals.css                       # Global styles
│
├── public/
│   └── assets/                           # Images, icons
│
├── .env.example
├── .env.local (gitignore)
├── next.config.js
├── tailwind.config.js
├── tsconfig.json
├── package.json
├── README.md
└── Dockerfile
```

---

## Database Schema (Supabase/PostgreSQL)

### Additional Table for Web Search Cache (NEW!)

```sql
CREATE TABLE web_search_cache (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
  query TEXT NOT NULL,
  
  -- Search results
  results JSONB NOT NULL,  -- Cached from Perplexity
  
  -- Metadata
  searched_at TIMESTAMP DEFAULT NOW(),
  expires_at TIMESTAMP,  -- Results expire after 1 week
  
  -- Usage tracking
  used_count INTEGER DEFAULT 0,  -- How many times this result was used
  last_used_at TIMESTAMP,
  
  UNIQUE(course_id, query)
);

CREATE INDEX idx_search_cache_course ON web_search_cache(course_id);
CREATE INDEX idx_search_cache_expires ON web_search_cache(expires_at);
```

### Updated generated_content Table

```sql
ALTER TABLE generated_content ADD COLUMN IF NOT EXISTS (
  -- Source tracking
  used_web_search BOOLEAN DEFAULT FALSE,
  web_search_query TEXT,                  -- Query used for web search
  web_sources JSONB DEFAULT '[]',         -- [{url, title, snippet, domain}]
  source_mix_ratio FLOAT                  -- % course materials vs web (0.0-1.0)
);
```

---

## API Endpoints Reference (Updated)

### Search Endpoints (Updated)

```
POST   /api/search/semantic        # Semantic search (course materials only)
  Body: { query: string, course_id: UUID, category?: 'theory'|'lab', limit?: 5 }
  Returns: { results: [...], took_ms: 234 }

POST   /api/search/hybrid          # Hybrid search (course + web)
  Body: { 
    query: string, 
    course_id: UUID, 
    include_web?: boolean,  # Default false (only if relevance < 40%)
    limit?: 5 
  }
  Returns: { 
    course_results: [...],
    web_results: [...],  # Only if triggered
    took_ms: 234
  }

POST   /api/search/web             # Force web search via Perplexity (NEW!)
  Body: { query: string, limit?: 5 }
  Returns: { results: [...], source: 'web', took_ms: 1200 }

GET    /api/search/filters         # Get available filters
GET    /api/search/suggestions     # Query autocomplete
```

### Generation Endpoints (Updated)

```
POST   /api/generate/theory        # Generate theory content
  Body: { topic: string, course_id: UUID, type: 'notes'|'summary', use_web?: true }
  Returns: { id: UUID, content: string, status: 'processing', sources: {...} }

POST   /api/generate/code          # Generate code examples
  Body: { topic: string, language: string, course_id: UUID, use_web?: true }
  Returns: { id: UUID, code: string, status: 'processing', sources: {...} }

GET    /api/generate/{id}/status   # Check generation status
  Returns: { status: string, content?, web_sources?, validation_status?, score? }
```

### Chat Endpoints (Updated)

```
POST   /api/chat/message           # Send message (streaming)
  Body: { session_id: UUID, message: string, include_web_search?: false }
  Returns: EventStream (SSE or WebSocket)
  
  # If include_web_search=true and relevance low:
  # Response includes: "Web search found additional info: ..."
```

### Web Search Endpoints (NEW!)

```
POST   /api/search/web             # Manual web search
  Body: { query: string, limit?: 5, cache?: true }
  Returns: { 
    results: [
      {
        title: string,
        url: string,
        snippet: string,
        relevance_score: float,
        source_domain: string,
        published_date: string
      }
    ],
    source: 'perplexity',
    cached: boolean,
    took_ms: number
  }

GET    /api/search/cache/clear     # Clear web search cache (admin only)
```

---

## Integration Workflow: Perplexity Web Search

### Scenario 1: Search with Low Relevance

```
User Query: "Latest developments in quantum computing"
    ↓
Search course materials → relevance = 35% (low)
    ↓
Trigger Perplexity web search automatically
    ↓
Combine results:
  - Course materials (0-3 results)
  - Web search (2-5 results)
    ↓
Display with clear labels:
  "📚 From Your Course Materials: ..."
  "🌐 Latest Research (from web): ..."
```

### Scenario 2: Generation with Web Augmentation

```
User Request: "Generate notes on React Hooks"
    ↓
Search course materials for React + Hooks
    ↓
If relevance < 50%:
  Trigger web search for "React Hooks latest"
    ↓
AI generates with context from:
  - Course materials (70% weight)
  - Web research (30% weight)
    ↓
Output shows:
  - Generated notes
  - Source attribution
  - Validation score
  - "Uses recent examples from web search: ✓"
```

### Scenario 3: Chat with Web Search Option

```
Student: "What's trending in AI right now?"
    ↓
Search course materials → relevance = 20% (too low)
    ↓
Chat response: "I found some info in course materials,
but this topic changes rapidly. 
Would you like me to search the web for latest news? (Y/N)"
    ↓
User: "Yes, search web"
    ↓
Trigger Perplexity search
    ↓
Response: "Based on recent news:
- OpenAI released... (source: openai.com)
- Anthropic announced... (source: anthropic.com)
- Plus context from your course materials..."
```

---

## Key Integration Points Summary

### Services Layer Updates

**search_service.py** → Now orchestrates hybrid search
```python
async def search_hybrid(query, course_id, include_web=None):
    # Search course materials
    course_results = await vectorstore_service.search(query, course_id)
    relevance = calculate_relevance(course_results)
    
    # Auto-trigger web search if low relevance
    if include_web is None:
        include_web = relevance < 0.40
    
    if include_web:
        web_results = await perplexity_service.search(query)
        return combine_results(course_results, web_results)
    
    return course_results
```

**generation_service.py** → Uses both sources for context
```python
async def generate_theory(topic, course_id, use_web=True):
    # Get course context
    course_context = await search_service.search(topic, course_id)
    
    # Get web context if needed
    if use_web and relevance_low:
        web_context = await perplexity_service.search(topic)
    
    # Generate with combined context
    content = await llm.generate(prompt, context=[course_context, web_context])
    
    # Track sources
    return {
        "content": content,
        "sources": {"course": course_sources, "web": web_sources}
    }
```

---

## Security & Cost Considerations

### Perplexity API Security

```python
# backend/app/core/mcp/perplexity_client.py

class PerplexitySearchService:
    async def search(self, query: str):
        # Rate limiting
        if self.check_rate_limit():
            raise RateLimitError("Too many searches")
        
        # Input validation
        if len(query) > 500:
            raise ValueError("Query too long")
        
        # Cache to reduce API calls
        cached = await cache.get(f"web_search:{query}")
        if cached and not expired(cached):
            return cached
        
        # Query Perplexity
        try:
            results = await self.client.search(query)
            
            # Cache result
            await cache.set(f"web_search:{query}", results, ttl=7*24*3600)
            
            # Log for monitoring
            logger.info(f"Web search: {query} - {len(results)} results")
            
            return results
        except Exception as e:
            logger.error(f"Perplexity search failed: {e}")
            raise
```

### Cost Optimization

```
Free tier (100 searches/month) sufficient for:
- Hackathon demo (20-30 searches)
- Testing phase (30-40 searches)
- Buffer (20 searches)

Strategy:
1. Cache all search results (7 days)
2. Only search if relevance < 40% (automatic)
3. Reuse results for similar queries
4. User must approve before web search
5. Monitor usage daily
```

---

## Technology Stack Summary (Updated)

### Backend
- **Framework**: FastAPI (Python 3.10+)
- **LLM Orchestration**: LangChain + LlamaIndex
- **Database**: Supabase (PostgreSQL + pgvector)
- **AI Models**: OpenAI (GPT-4o-mini, text-embedding-3-small)
- **Web Search**: Perplexity API (NEW!)
- **Document Processing**: PyPDF2, python-docx, python-pptx
- **Code Analysis**: tree-sitter, ast
- **Async**: asyncio, httpx
- **Caching**: Redis (optional) or in-memory cache

### Frontend
- **Framework**: Next.js 14 (React 18)
- **UI Library**: shadcn/ui + Tailwind CSS
- **API Client**: Axios/Fetch
- **Database Client**: @supabase/supabase-js
- **State Management**: React Hooks
- **Markdown**: react-markdown + syntax-highlighter

### External Services
- OpenAI API (Chat, embeddings)
- Perplexity API (Web search) - NEW!
- Supabase (Database + Storage)

### Deployment
- **Backend**: Railway, Render, or DigitalOcean
- **Frontend**: Vercel or Netlify
- **Database**: Supabase Cloud
- **Storage**: Supabase Storage (S3-compatible)

---

## Environment Variables (.env)

```bash
# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_CHAT_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJ...
SUPABASE_SERVICE_KEY=eyJ...

# Perplexity (NEW!)
PERPLEXITY_API_KEY=pplx-...
PERPLEXITY_RATE_LIMIT=5  # Searches per minute

# App
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000
LOG_LEVEL=INFO
```

---

## Performance Expectations

```
Search (course materials only):    < 2 seconds
Search (with web search):          < 4 seconds (2s materials + 2s web)
Generation (from materials):       30-60 seconds
Generation (with web context):     45-90 seconds (extra 15-30s for web search)
Chat response:                     5 seconds (streaming)
Web search only:                   1-2 seconds
```

---

## Monitoring & Logging (Updated)

### Metrics to Track
- API response times (by endpoint)
- Embedding generation time
- Chat response latency
- Generation quality score
- Error rates by endpoint
- **NEW:** Web search API calls and latency
- **NEW:** Web search cache hit rate
- **NEW:** Average relevance score when web search triggered
- OpenAI API usage and costs
- Perplexity API usage and costs
- Supabase storage/bandwidth usage

### Key Logs
```
[INFO] Web search triggered: query="...", relevance=0.35
[INFO] Web search cache hit: query="...", results=5
[ERROR] Perplexity API rate limited, retrying...
[DEBUG] Web search took 1234ms, returned 5 results
[INFO] Generated content used web sources: 30% web, 70% course
```

---

## Testing Web Search Integration

### Unit Tests

```python
# tests/test_web_search.py

@pytest.mark.asyncio
async def test_web_search_basic():
    service = PerplexitySearchService()
    results = await service.search("Python async/await")
    assert len(results) > 0
    assert all(r['url'] for r in results)

@pytest.mark.asyncio
async def test_web_search_cache():
    service = PerplexitySearchService()
    
    # First search
    results1 = await service.search("React Hooks")
    
    # Second search (should use cache)
    results2 = await service.search("React Hooks")
    
    assert results1 == results2
    assert mocked_api.call_count == 1  # Only called once

@pytest.mark.asyncio
async def test_hybrid_search_low_relevance():
    search_service = SearchService()
    
    # Mock low relevance course search
    with patch('course_search', return_value=[]):
        results = await search_service.search_hybrid("test", course_id)
        
        # Should have triggered web search
        assert 'web_results' in results
```

---

## Summary: What's New with Perplexity

✅ **Automatic web augmentation** when course materials insufficient
✅ **Explicit web search** option for students
✅ **Caching** to reduce API calls and costs
✅ **Clear source attribution** (course vs web)
✅ **Smart triggers** (auto-detect when web search needed)
✅ **Hybrid results** combining course + web sources
✅ **Low cost** (free tier sufficient for hackathon)
✅ **Better generation** with access to latest information

This makes your platform more powerful while keeping it simple and cost-effective!
