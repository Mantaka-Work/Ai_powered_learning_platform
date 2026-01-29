-- ===========================================
-- AI-Powered Learning Platform Database Schema
-- Supabase PostgreSQL with pgvector
-- ===========================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

-- ===========================================
-- TABLES
-- ===========================================

-- Courses table
CREATE TABLE IF NOT EXISTS courses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Materials table (uploaded course content)
CREATE TABLE IF NOT EXISTS materials (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    file_path VARCHAR(1000) NOT NULL,
    file_type VARCHAR(20) NOT NULL,
    file_size INTEGER NOT NULL,
    category VARCHAR(20) NOT NULL CHECK (category IN ('theory', 'lab')),
    week_number INTEGER CHECK (week_number >= 1 AND week_number <= 52),
    tags TEXT[] DEFAULT '{}',
    programming_language VARCHAR(50),
    uploaded_by UUID,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Document embeddings table (pgvector)
CREATE TABLE IF NOT EXISTS document_embeddings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    material_id UUID NOT NULL REFERENCES materials(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    embedding vector(1536), -- text-embedding-3-small dimension
    chunk_index INTEGER NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Chat sessions table
CREATE TABLE IF NOT EXISTS chat_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    title VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Chat messages table
CREATE TABLE IF NOT EXISTS chat_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    sources JSONB DEFAULT '[]',
    used_web_search BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Generated content table
CREATE TABLE IF NOT EXISTS generated_content (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    user_id UUID,
    type VARCHAR(50) NOT NULL,
    topic VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    programming_language VARCHAR(50),
    validation_status VARCHAR(20) CHECK (validation_status IN ('validated', 'warning', 'failed')),
    validation_score FLOAT,
    validation_details JSONB DEFAULT '{}',
    sources JSONB DEFAULT '{}',
    used_web_search BOOLEAN DEFAULT FALSE,
    web_sources JSONB DEFAULT '[]',
    source_mix_ratio FLOAT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Web search cache table
CREATE TABLE IF NOT EXISTS web_search_cache (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    query_hash VARCHAR(64) UNIQUE NOT NULL,
    query TEXT NOT NULL,
    results JSONB NOT NULL,
    provider VARCHAR(50) DEFAULT 'perplexity',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ===========================================
-- INDEXES
-- ===========================================

-- Materials indexes
CREATE INDEX IF NOT EXISTS idx_materials_course_id ON materials(course_id);
CREATE INDEX IF NOT EXISTS idx_materials_category ON materials(category);
CREATE INDEX IF NOT EXISTS idx_materials_week ON materials(week_number);
CREATE INDEX IF NOT EXISTS idx_materials_file_type ON materials(file_type);

-- Embeddings indexes
CREATE INDEX IF NOT EXISTS idx_embeddings_material_id ON document_embeddings(material_id);

-- Vector similarity search index (IVFFlat for faster searches)
CREATE INDEX IF NOT EXISTS idx_embeddings_vector ON document_embeddings 
USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Chat indexes
CREATE INDEX IF NOT EXISTS idx_chat_sessions_user ON chat_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_course ON chat_sessions(course_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_session ON chat_messages(session_id);

-- Generated content indexes
CREATE INDEX IF NOT EXISTS idx_generated_course ON generated_content(course_id);
CREATE INDEX IF NOT EXISTS idx_generated_user ON generated_content(user_id);
CREATE INDEX IF NOT EXISTS idx_generated_type ON generated_content(type);

-- Web search cache index
CREATE INDEX IF NOT EXISTS idx_web_cache_hash ON web_search_cache(query_hash);
CREATE INDEX IF NOT EXISTS idx_web_cache_created ON web_search_cache(created_at);

-- ===========================================
-- FUNCTIONS
-- ===========================================

-- Function for vector similarity search
CREATE OR REPLACE FUNCTION match_documents(
    query_embedding vector(1536),
    match_count INT DEFAULT 10,
    filter_course_id UUID DEFAULT NULL,
    similarity_threshold FLOAT DEFAULT 0.5
)
RETURNS TABLE (
    id UUID,
    material_id UUID,
    content TEXT,
    chunk_index INTEGER,
    metadata JSONB,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        de.id,
        de.material_id,
        de.content,
        de.chunk_index,
        de.metadata,
        1 - (de.embedding <=> query_embedding) AS similarity
    FROM document_embeddings de
    JOIN materials m ON de.material_id = m.id
    WHERE 
        (filter_course_id IS NULL OR m.course_id = filter_course_id)
        AND 1 - (de.embedding <=> query_embedding) > similarity_threshold
    ORDER BY de.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Function to count embeddings by course
CREATE OR REPLACE FUNCTION count_embeddings_by_course(p_course_id UUID)
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    result INTEGER;
BEGIN
    SELECT COUNT(de.id) INTO result
    FROM document_embeddings de
    JOIN materials m ON de.material_id = m.id
    WHERE m.course_id = p_course_id;
    
    RETURN result;
END;
$$;

-- ===========================================
-- ROW LEVEL SECURITY (RLS)
-- ===========================================

-- Enable RLS on tables
ALTER TABLE courses ENABLE ROW LEVEL SECURITY;
ALTER TABLE materials ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE generated_content ENABLE ROW LEVEL SECURITY;

-- Policies for public read access to courses and materials
CREATE POLICY "Allow public read access to courses" ON courses
    FOR SELECT USING (true);

CREATE POLICY "Allow public read access to materials" ON materials
    FOR SELECT USING (true);

-- Policies for authenticated user access to their own chat sessions
CREATE POLICY "Users can view their own chat sessions" ON chat_sessions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create their own chat sessions" ON chat_sessions
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete their own chat sessions" ON chat_sessions
    FOR DELETE USING (auth.uid() = user_id);

-- Policies for chat messages (through session ownership)
CREATE POLICY "Users can view messages in their sessions" ON chat_messages
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM chat_sessions 
            WHERE chat_sessions.id = chat_messages.session_id 
            AND chat_sessions.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can create messages in their sessions" ON chat_messages
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM chat_sessions 
            WHERE chat_sessions.id = chat_messages.session_id 
            AND chat_sessions.user_id = auth.uid()
        )
    );

-- Policies for generated content
CREATE POLICY "Users can view their generated content" ON generated_content
    FOR SELECT USING (user_id IS NULL OR auth.uid() = user_id);

CREATE POLICY "Users can create generated content" ON generated_content
    FOR INSERT WITH CHECK (user_id IS NULL OR auth.uid() = user_id);

-- ===========================================
-- STORAGE BUCKETS (run in Supabase dashboard)
-- ===========================================

-- Note: Execute these in the Supabase SQL editor or dashboard

-- INSERT INTO storage.buckets (id, name, public)
-- VALUES ('course-materials', 'course-materials', false);

-- INSERT INTO storage.buckets (id, name, public)
-- VALUES ('exports', 'exports', false);

-- Storage policies
-- CREATE POLICY "Allow authenticated uploads" ON storage.objects
--     FOR INSERT WITH CHECK (bucket_id = 'course-materials' AND auth.role() = 'authenticated');

-- CREATE POLICY "Allow authenticated downloads" ON storage.objects
--     FOR SELECT USING (bucket_id = 'course-materials' AND auth.role() = 'authenticated');
