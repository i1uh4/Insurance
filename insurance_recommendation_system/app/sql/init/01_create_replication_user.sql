DO $$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'replicator') THEN
      CREATE USER replicator WITH REPLICATION ENCRYPTED PASSWORD 'replicator_password';
      RAISE NOTICE 'Replication user created successfully';
   ELSE
      RAISE NOTICE 'Replication user already exists';
   END IF;
END
$$;