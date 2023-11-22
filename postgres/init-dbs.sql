SELECT 'CREATE DATABASE db_oxygen'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'db_oxygen')\gexec ;

SELECT 'CREATE DATABASE db_postgres'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'db_postgres')\gexec;