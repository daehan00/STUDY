-- Create a new user with read-only access
CREATE USER readonly_pg_user WITH PASSWORD 'readonly_pg_password';

-- Grant connection to the database
GRANT CONNECT ON DATABASE test_pgdb TO readonly_pg_user;

-- Grant usage on schema public
GRANT USAGE ON SCHEMA public TO readonly_pg_user;

-- Grant SELECT on all tables in public schema
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly_pg_user;

-- Ensure future tables are also readable
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO readonly_pg_user;
