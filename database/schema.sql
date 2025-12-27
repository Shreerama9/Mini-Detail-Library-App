-- Table: details
CREATE TABLE details (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    tags TEXT[] NOT NULL,
    description TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

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


-- If using free supabase database, first run this file in SQL editor 