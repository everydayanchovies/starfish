#!/usr/bin/env bash

set -x

cp db.sqlite db_pre_migration.sqlite

sqlite3 db.sqlite < ./scripts/migrationtodjango32/db_resolve_issues.sql

python3 manage.py migrate
