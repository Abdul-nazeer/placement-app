-- Initialize PlacementPrep Database
-- This script runs when the PostgreSQL container starts

-- Create database if it doesn't exist
SELECT 'CREATE DATABASE placement_prep'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'placement_prep')\gexec

-- Connect to the database
\c placement_prep;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create initial admin user (will be handled by application later)
-- This is just a placeholder for database initialization