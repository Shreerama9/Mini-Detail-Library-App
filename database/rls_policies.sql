CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('admin', 'architect')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

INSERT INTO users (email, role) VALUES
    ('admin@piaxis.com', 'admin'),
    ('architect@piaxis.com', 'architect')
ON CONFLICT (email) DO NOTHING;

ALTER TABLE details ADD COLUMN IF NOT EXISTS created_by INTEGER REFERENCES users(id);

ALTER TABLE details ENABLE ROW LEVEL SECURITY;

CREATE POLICY admin_see_all ON details
    FOR SELECT
    TO PUBLIC
    USING (
        current_setting('app.current_user_role', true) = 'admin'
    );

CREATE POLICY architect_see_standard ON details
    FOR SELECT
    TO PUBLIC
    USING (
        current_setting('app.current_user_role', true) = 'architect'
        AND (source = 'standard' OR source IS NULL)
    );

CREATE POLICY allow_when_no_role ON details
    FOR SELECT
    TO PUBLIC
    USING (
        current_setting('app.current_user_role', true) IS NULL
        OR current_setting('app.current_user_role', true) = ''
    );
