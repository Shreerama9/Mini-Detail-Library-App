#!/bin/bash

# PiAxis Mini Detail Library - Database Setup Script
# This script sets up the PostgreSQL database with schema, RLS policies, and seed data

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}PiAxis Detail Library - Database Setup${NC}"
echo -e "${GREEN}========================================${NC}\n"

# Default values
DB_NAME="${DB_NAME:-piaxis_db}"
DB_USER="${DB_USER:-postgres}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"

# Ask for database password if not set
if [ -z "$DB_PASSWORD" ]; then
    echo -e "${YELLOW}Enter PostgreSQL password for user '$DB_USER':${NC}"
    read -s DB_PASSWORD
    echo
fi

export PGPASSWORD=$DB_PASSWORD

echo -e "${YELLOW}Configuration:${NC}"
echo "  Database: $DB_NAME"
echo "  User: $DB_USER"
echo "  Host: $DB_HOST"
echo "  Port: $DB_PORT"
echo

# Check if PostgreSQL is accessible
echo -e "${YELLOW}[1/6] Checking PostgreSQL connection...${NC}"
if psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres -c '\q' 2>/dev/null; then
    echo -e "${GREEN}✓ PostgreSQL connection successful${NC}"
else
    echo -e "${RED}✗ Failed to connect to PostgreSQL${NC}"
    echo -e "${RED}Please check your credentials and ensure PostgreSQL is running${NC}"
    exit 1
fi

# Check if database exists, drop if it does (for clean setup)
echo -e "\n${YELLOW}[2/6] Checking if database exists...${NC}"
DB_EXISTS=$(psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'")

if [ "$DB_EXISTS" = "1" ]; then
    echo -e "${YELLOW}Database '$DB_NAME' already exists.${NC}"
    read -p "Do you want to drop and recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Dropping database '$DB_NAME'...${NC}"
        psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres -c "DROP DATABASE $DB_NAME;"
        echo -e "${GREEN}✓ Database dropped${NC}"
    else
        echo -e "${YELLOW}Skipping database creation. Will apply schema to existing database.${NC}"
    fi
fi

# Create database if it doesn't exist
if [ "$DB_EXISTS" != "1" ] || [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "\n${YELLOW}[3/6] Creating database '$DB_NAME'...${NC}"
    psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres -c "CREATE DATABASE $DB_NAME;"
    echo -e "${GREEN}✓ Database created${NC}"
else
    echo -e "\n${YELLOW}[3/6] Using existing database '$DB_NAME'${NC}"
fi

# Enable pgvector extension
echo -e "\n${YELLOW}[4/6] Setting up pgvector extension...${NC}"
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "CREATE EXTENSION IF NOT EXISTS vector;"
echo -e "${GREEN}✓ pgvector extension enabled${NC}"

# Apply schema
echo -e "\n${YELLOW}[5/6] Applying database schema...${NC}"
if [ -f "schema.sql" ]; then
    psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f schema.sql
    echo -e "${GREEN}✓ Schema applied successfully${NC}"
else
    echo -e "${RED}✗ schema.sql not found in current directory${NC}"
    exit 1
fi

# Apply RLS policies
echo -e "\n${YELLOW}[5.5/6] Applying Row-Level Security policies...${NC}"
if [ -f "rls_policies.sql" ]; then
    psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f rls_policies.sql
    echo -e "${GREEN}✓ RLS policies applied successfully${NC}"
else
    echo -e "${RED}✗ rls_policies.sql not found in current directory${NC}"
    exit 1
fi

# Apply seed data
echo -e "\n${YELLOW}[6/6] Loading seed data...${NC}"
if [ -f "seed.sql" ]; then
    psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f seed.sql
    echo -e "${GREEN}✓ Seed data loaded successfully${NC}"
else
    echo -e "${RED}✗ seed.sql not found in current directory${NC}"
    exit 1
fi

# Verify setup
echo -e "\n${YELLOW}Verifying setup...${NC}"
TABLE_COUNT=$(psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -tAc "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE';")
DETAIL_COUNT=$(psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -tAc "SELECT COUNT(*) FROM details;")
USER_COUNT=$(psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -tAc "SELECT COUNT(*) FROM users;")
POLICY_COUNT=$(psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -tAc "SELECT COUNT(*) FROM pg_policies WHERE tablename='details';")

echo -e "${GREEN}Setup Summary:${NC}"
echo "  Tables created: $TABLE_COUNT"
echo "  Details loaded: $DETAIL_COUNT"
echo "  Users created: $USER_COUNT"
echo "  RLS policies: $POLICY_COUNT"

# Test RLS policies
echo -e "\n${YELLOW}Testing RLS policies...${NC}"

# Test admin access
ADMIN_COUNT=$(psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -tAc "
BEGIN;
SET LOCAL app.current_user_role = 'admin';
SELECT COUNT(*) FROM details;
COMMIT;
")
echo "  Admin can see: $ADMIN_COUNT details"

# Test architect access
ARCHITECT_COUNT=$(psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -tAc "
BEGIN;
SET LOCAL app.current_user_role = 'architect';
SELECT COUNT(*) FROM details;
COMMIT;
")
echo "  Architect can see: $ARCHITECT_COUNT details"

if [ "$ADMIN_COUNT" -gt "$ARCHITECT_COUNT" ]; then
    echo -e "${GREEN}✓ RLS policies are working correctly!${NC}"
else
    echo -e "${YELLOW}⚠ RLS policies may not be working as expected${NC}"
fi

# Generate DATABASE_URL
echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}Setup Complete!${NC}"
echo -e "${GREEN}========================================${NC}\n"

echo -e "${YELLOW}Add this to your backend/.env file:${NC}"
echo "DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME"

echo -e "\n${YELLOW}Test users available:${NC}"
echo "  Admin: admin@piaxis.com (role: admin)"
echo "  Architect: architect@piaxis.com (role: architect)"

echo -e "\n${YELLOW}Next steps:${NC}"
echo "1. Copy the DATABASE_URL to your backend/.env file"
echo "2. Start the backend: cd ../backend && python main.py"
echo "3. Test RLS endpoint: curl -H 'X-USER-ROLE: admin' http://localhost:8000/security/details"

echo -e "\n${GREEN}Happy coding! 🚀${NC}\n"
