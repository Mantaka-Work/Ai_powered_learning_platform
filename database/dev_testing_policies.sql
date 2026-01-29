-- ===========================================
-- Development/Testing RLS Policies
-- Run this in Supabase SQL Editor after schema.sql
-- This allows anonymous access for testing purposes
-- ===========================================

-- Drop existing restrictive policies for development testing
DROP POLICY IF EXISTS "Allow public read access to courses" ON courses;
DROP POLICY IF EXISTS "Allow public read access to materials" ON materials;

-- Create permissive policies for courses (allow all operations for testing)
CREATE POLICY "Allow all operations on courses" ON courses
    FOR ALL USING (true) WITH CHECK (true);

-- Create permissive policies for materials (allow all operations for testing)  
CREATE POLICY "Allow all operations on materials" ON materials
    FOR ALL USING (true) WITH CHECK (true);

-- Permissive policies for document_embeddings
ALTER TABLE document_embeddings ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow all operations on embeddings" ON document_embeddings
    FOR ALL USING (true) WITH CHECK (true);

-- Update chat sessions policy to allow anonymous access for testing
DROP POLICY IF EXISTS "Users can view their own chat sessions" ON chat_sessions;
DROP POLICY IF EXISTS "Users can create their own chat sessions" ON chat_sessions;
DROP POLICY IF EXISTS "Users can delete their own chat sessions" ON chat_sessions;

CREATE POLICY "Allow all operations on chat_sessions" ON chat_sessions
    FOR ALL USING (true) WITH CHECK (true);

-- Update chat messages policy
DROP POLICY IF EXISTS "Users can view messages in their sessions" ON chat_messages;
DROP POLICY IF EXISTS "Users can create messages in their sessions" ON chat_messages;

CREATE POLICY "Allow all operations on chat_messages" ON chat_messages
    FOR ALL USING (true) WITH CHECK (true);

-- Update generated content policy
DROP POLICY IF EXISTS "Users can view their generated content" ON generated_content;
DROP POLICY IF EXISTS "Users can create generated content" ON generated_content;

CREATE POLICY "Allow all operations on generated_content" ON generated_content
    FOR ALL USING (true) WITH CHECK (true);

-- Web search cache (enable RLS and set permissive policy)
ALTER TABLE web_search_cache ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow all operations on web_search_cache" ON web_search_cache
    FOR ALL USING (true) WITH CHECK (true);

-- ===========================================
-- NOTE: REVERT THESE POLICIES IN PRODUCTION!
-- ===========================================
