#!/bin/bash
set -e

DB_NAME="voseq"
POSTGRES_USER="postgres"

echo "CREATING ${DB_NAME} DB for admin user ${POSTGRES_USER}"
echo "------"

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE DATABASE $DB_NAME;
EOSQL
