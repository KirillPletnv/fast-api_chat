CREATE DATABASE my_postgres;

DO $$
BEGIN
    IF EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'test_user') THEN       
        ALTER USER test_user WITH PASSWORD 'test1234';
    ELSE
        CREATE USER test_user WITH PASSWORD 'test1234';
    END IF;
END $$;

GRANT ALL PRIVILEGES ON DATABASE my_postgres TO test_user;
