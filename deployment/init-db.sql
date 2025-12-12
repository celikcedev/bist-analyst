-- =============================================================================
-- BIST Analyst - Database Initialization Script
-- =============================================================================
-- This script runs when the PostgreSQL container is first created
-- It creates the initial schema if not exists

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Note: The actual tables are created by Alembic migrations
-- This script is for any initial setup that needs to happen before migrations

-- Grant privileges (if using a non-root user in the future)
-- GRANT ALL PRIVILEGES ON DATABASE bist_analyst TO bist_user;

-- Log that initialization is complete
DO $$
BEGIN
    RAISE NOTICE 'Database initialization complete. Run Alembic migrations next.';
END $$;

