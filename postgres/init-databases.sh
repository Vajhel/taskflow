#!/bin/bash
set -e

# Создание баз данных для каждого микросервиса
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE DATABASE auth_db;
    CREATE DATABASE tasks_db;
    CREATE DATABASE notifications_db;
EOSQL

echo "Базы данных auth_db, tasks_db, notifications_db успешно созданы."
