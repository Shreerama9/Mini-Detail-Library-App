CREATE EXTENSION IF NOT EXISTS vector;

-- Table 1: details
CREATE TABLE details (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    tags TEXT[] NOT NULL,
    description TEXT NOT NULL,
    embedding vector(384),              
    source VARCHAR(50) DEFAULT 'standard',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_details_embedding ON details USING ivfflat (embedding vector_cosine_ops);


-- Table: details_usage_rules
CREATE TABLE detail_usage_rules (
    id SERIAL PRIMARY KEY,
    detail_id INTEGER NOT NULL REFERENCES details(id) ON DELETE CASCADE,
    host_element VARCHAR(100) NOT NULL,
    adjacent_element VARCHAR(100) NOT NULL,
    exposure VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for faster lookups
CREATE INDEX idx_detail_usage_rules_lookup 
ON detail_usage_rules(host_element, adjacent_element, exposure);


