-- ECMA-376 Documentation Database Schema
-- Designed to store hierarchical document structure with 5-level depth and embeddings

-- Drop existing tables if they exist
DROP TABLE IF EXISTS ecma_sections CASCADE;
DROP EXTENSION IF EXISTS vector;

-- Enable vector extension for embeddings (install with: CREATE EXTENSION vector;)
-- CREATE EXTENSION IF NOT EXISTS vector;

-- Main table for storing hierarchical sections
CREATE TABLE ecma_sections (
    id SERIAL PRIMARY KEY,
    
    -- 5-level hierarchy fields
    level1 TEXT,           -- e.g., "20"
    level2 TEXT,           -- e.g., "20.1"
    level3 TEXT,           -- e.g., "20.1.2"
    level4 TEXT,           -- e.g., "20.1.2.2"
    level5 TEXT,           -- e.g., "20.1.2.2.1"
    
    -- Full section number (for easier querying)
    full_section_number TEXT NOT NULL,
    
    -- Title and description
    title TEXT NOT NULL,
    description TEXT,
    
    -- Metadata
    page_reference TEXT,   -- Page number reference from document
    section_type VARCHAR(50), -- e.g., 'heading', 'subheading', 'element', 'property'
    
    -- Hierarchy depth (1-5)
    depth INTEGER NOT NULL CHECK (depth >= 1 AND depth <= 5),
    
    -- Parent-child relationship (self-referencing)
    parent_id INTEGER REFERENCES ecma_sections(id),
    
    -- Embedding vector for semantic search (384 dimensions for sentence-transformers)
    -- Using TEXT to store JSON array until pgvector is available
    embedding_vector TEXT,  -- Will store JSON array of floats
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_ecma_sections_full_number ON ecma_sections(full_section_number);
CREATE INDEX idx_ecma_sections_level1 ON ecma_sections(level1);
CREATE INDEX idx_ecma_sections_level2 ON ecma_sections(level2);
CREATE INDEX idx_ecma_sections_level3 ON ecma_sections(level3);
CREATE INDEX idx_ecma_sections_level4 ON ecma_sections(level4);
CREATE INDEX idx_ecma_sections_level5 ON ecma_sections(level5);
CREATE INDEX idx_ecma_sections_depth ON ecma_sections(depth);
CREATE INDEX idx_ecma_sections_parent_id ON ecma_sections(parent_id);
CREATE INDEX idx_ecma_sections_title ON ecma_sections USING gin(to_tsvector('english', title));
CREATE INDEX idx_ecma_sections_description ON ecma_sections USING gin(to_tsvector('english', description));

-- Function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to automatically update updated_at
CREATE TRIGGER update_ecma_sections_updated_at 
    BEFORE UPDATE ON ecma_sections 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- View for easy hierarchical queries
CREATE VIEW ecma_hierarchy AS
SELECT 
    id,
    full_section_number,
    title,
    description,
    depth,
    CASE 
        WHEN depth = 1 THEN level1
        WHEN depth = 2 THEN level2
        WHEN depth = 3 THEN level3
        WHEN depth = 4 THEN level4
        WHEN depth = 5 THEN level5
    END as current_level,
    parent_id,
    page_reference
FROM ecma_sections
ORDER BY 
    CASE WHEN level1 IS NOT NULL THEN level1::numeric ELSE 999 END,
    CASE WHEN level2 IS NOT NULL THEN SUBSTRING(level2 FROM '\\.([0-9]+)')::numeric ELSE 999 END,
    CASE WHEN level3 IS NOT NULL THEN SUBSTRING(level3 FROM '\\.([0-9]+)$')::numeric ELSE 999 END,
    CASE WHEN level4 IS NOT NULL THEN SUBSTRING(level4 FROM '\\.([0-9]+)$')::numeric ELSE 999 END,
    CASE WHEN level5 IS NOT NULL THEN SUBSTRING(level5 FROM '\\.([0-9]+)$')::numeric ELSE 999 END;

-- Function to find all children of a section
CREATE OR REPLACE FUNCTION get_section_children(section_id INTEGER)
RETURNS TABLE(
    id INTEGER,
    full_section_number TEXT,
    title TEXT,
    depth INTEGER
) AS $$
BEGIN
    RETURN QUERY
    WITH RECURSIVE children AS (
        SELECT s.id, s.full_section_number, s.title, s.depth
        FROM ecma_sections s
        WHERE s.id = section_id
        
        UNION ALL
        
        SELECT s.id, s.full_section_number, s.title, s.depth
        FROM ecma_sections s
        INNER JOIN children c ON s.parent_id = c.id
    )
    SELECT c.id, c.full_section_number, c.title, c.depth
    FROM children c
    WHERE c.id != section_id
    ORDER BY c.full_section_number;
END;
$$ LANGUAGE plpgsql;

-- Function to get section path (breadcrumb)
CREATE OR REPLACE FUNCTION get_section_path(section_id INTEGER)
RETURNS TABLE(
    id INTEGER,
    full_section_number TEXT,
    title TEXT,
    depth INTEGER
) AS $$
BEGIN
    RETURN QUERY
    WITH RECURSIVE path AS (
        SELECT s.id, s.full_section_number, s.title, s.depth, s.parent_id
        FROM ecma_sections s
        WHERE s.id = section_id
        
        UNION ALL
        
        SELECT s.id, s.full_section_number, s.title, s.depth, s.parent_id
        FROM ecma_sections s
        INNER JOIN path p ON s.id = p.parent_id
    )
    SELECT p.id, p.full_section_number, p.title, p.depth
    FROM path p
    ORDER BY p.depth;
END;
$$ LANGUAGE plpgsql;