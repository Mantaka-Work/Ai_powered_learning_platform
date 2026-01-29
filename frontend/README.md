# AI-Powered Learning Platform Frontend

## Quick Start

1. Install dependencies:
```bash
npm install
```

2. Copy `.env.example` to `.env.local` and fill in your values

3. Run the development server:
```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000)

## Project Structure

```
frontend/
├── app/                    # Next.js App Router
│   ├── layout.tsx         # Root layout
│   ├── page.tsx           # Home page
│   ├── globals.css        # Global styles
│   └── (dashboard)/       # Dashboard routes
│       └── courses/[id]/  # Course pages
├── components/
│   ├── ui/                # shadcn/ui components
│   ├── Chat/              # Chat interface
│   ├── Search/            # Search interface
│   ├── Generation/        # Content generation
│   └── Materials/         # File upload
├── hooks/                  # Custom React hooks
├── lib/
│   ├── api.ts             # API client
│   ├── supabase.ts        # Supabase client
│   └── utils.ts           # Utility functions
└── public/                 # Static assets
```

## Features

- **Search** - Semantic search with web fallback
- **Generation** - AI-generated notes and code
- **Chat** - Conversational AI assistant
- **Materials** - File upload and management

## Tech Stack

- Next.js 14 (App Router)
- React 18
- TypeScript
- Tailwind CSS
- shadcn/ui components
- Supabase Auth
