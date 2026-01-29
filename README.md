# AI-Powered Supplementary Learning Platform

An AI-powered university course learning platform with RAG-based search, content generation, and conversational AI.

## 🚀 Features

- **📚 Content Management** - Upload and manage course materials (PDF, PPTX, DOCX, code files)
- **🔍 Semantic Search** - RAG-based search with pgvector embeddings
- **🌐 Web Search Fallback** - Perplexity API integration when course relevance < 40%
- **✨ AI Generation** - Generate notes, summaries, and code examples
- **💬 Chat Interface** - Conversational AI with course context
- **✅ Validation** - Syntax checking and content grounding validation

## 📋 Prerequisites

- **Python 3.10+** (tested with 3.13)
- **Node.js 18+**
- **npm** or **yarn**
- **Supabase Account** (for database & storage)
- **OpenAI API Key**
- **Perplexity API Key** (optional, for web search)

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | FastAPI, Python, LangChain |
| Frontend | Next.js 14, React, Tailwind CSS, shadcn/ui |
| Database | Supabase (PostgreSQL + pgvector) |
| AI | OpenAI GPT-4o-mini, text-embedding-3-small |
| Web Search | Perplexity API |

---

## ⚙️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/Mantaka-Work/Ai_powered_learning_platform.git
cd Ai_powered_learning_platform
```

### 2. Database Setup (Supabase)

1. Create a new project at [supabase.com](https://supabase.com)
2. Go to **SQL Editor** in your Supabase dashboard
3. Copy the contents of `database/schema.sql` and run it
4. This creates all tables, indexes, functions, and RLS policies

### 3. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Configure Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key
OPENAI_CHAT_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_SERVICE_KEY=your-supabase-service-key

# Perplexity Configuration (optional)
PERPLEXITY_API_KEY=your-perplexity-api-key
PERPLEXITY_RATE_LIMIT=5

# Application Settings
APP_NAME=AI Learning Platform
APP_VERSION=1.0.0
DEBUG=true
LOG_LEVEL=INFO

# Security
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Allowed Origins
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### 4. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Install additional required packages (if not already installed)
npm install tailwindcss-animate
```

#### Configure Environment Variables

Create a `.env.local` file in the `frontend/` directory:

```env
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-supabase-anon-key
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 🏃 Running the Application

### Start Backend Server

```bash
# From the backend directory (with venv activated)
cd backend
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: **http://localhost:8000**

### Start Frontend Server

```bash
# From the frontend directory (in a new terminal)
cd frontend
npm run dev
```

Frontend will be available at: **http://localhost:3000**

---

## 📚 API Documentation

Once the backend is running, access the interactive API docs:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

### Key API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Check service health |
| `/api/courses` | GET/POST | List/create courses |
| `/api/materials/upload` | POST | Upload course materials |
| `/api/search/semantic` | POST | Semantic search in course materials |
| `/api/search/hybrid` | POST | Search with web fallback |
| `/api/generate/theory` | POST | Generate notes/summaries |
| `/api/generate/code` | POST | Generate code examples |
| `/api/chat/message` | POST | Send chat message |

---

## 📁 Project Structure

```
├── backend/
│   ├── app/
│   │   ├── api/routes/       # API endpoints
│   │   ├── core/
│   │   │   ├── rag/          # RAG pipeline (embeddings, retriever, chains)
│   │   │   ├── generation/   # Content generators
│   │   │   ├── validation/   # Code & content validators
│   │   │   ├── mcp/          # Perplexity web search
│   │   │   └── document_processing/  # Parsers & chunking
│   │   ├── db/               # Database repositories
│   │   ├── services/         # Business logic
│   │   └── utils/            # Utilities
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── app/                  # Next.js app router
│   ├── components/           # React components
│   ├── hooks/                # Custom hooks
│   ├── lib/                  # Utilities & API client
│   └── .env.local
├── database/
│   └── schema.sql            # PostgreSQL schema
└── README.md
```

---

## 🔧 Troubleshooting

### Backend won't start
- Ensure virtual environment is activated
- Check that all environment variables are set in `.env`
- Verify Python version: `python --version` (needs 3.10+)

### Frontend compilation errors
- Run `npm install` to ensure all dependencies are installed
- Check `.env.local` has correct Supabase credentials

### Database connection issues
- Verify Supabase URL and keys in environment files
- Ensure the schema has been run in Supabase SQL Editor
- Check that pgvector extension is enabled

### LangChain import errors
- Ensure you're using the latest packages: `pip install -U langchain langchain-openai langchain-core`

---

## 🔑 Getting API Keys

### OpenAI
1. Go to [platform.openai.com](https://platform.openai.com)
2. Navigate to API Keys section
3. Create a new secret key

### Supabase
1. Go to [supabase.com](https://supabase.com) and create a project
2. Go to Project Settings → API
3. Copy the **URL**, **anon key**, and **service_role key**

### Perplexity (Optional)
1. Go to [perplexity.ai](https://www.perplexity.ai)
2. Navigate to API settings
3. Generate an API key

---

## 📄 License

MIT License - feel free to use this project for learning and development.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request
