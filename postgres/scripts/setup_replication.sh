#!/bin/bash

echo "=== Starting Replication Setup ==="


echo "Waiting for master database..."
until pg_isready -h db_master -p 5432 -U insurance; do
    echo "Master not ready, waiting..."
    sleep 2
done

echo "Master database is ready!"


echo "Testing replication user connection..."
export PGPASSWORD=replicator_password


if psql -h db_master -p 5432 -U replicator -d postgres -c "SELECT 1;" 2>/dev/null; then
    echo "✓ Replication user connection successful"
else
    echo "✗ Failed to connect as replication user"
    echo "Attempting to create replication user..."
    
    
    export PGPASSWORD=postgres
    psql -h db_master -p 5432 -U postgres -d postgres -c "
        DO \$\$
        BEGIN
           IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'replicator') THEN
              CREATE USER replicator WITH REPLICATION ENCRYPTED PASSWORD 'replicator_password';
              RAISE NOTICE 'Replication user created';
           END IF;
        END
        \$\$;
    "
    
    
    export PGPASSWORD=replicator_password
    if psql -h db_master -p 5432 -U replicator -d postgres -c "SELECT 1;" 2>/dev/null; then
        echo "✓ Replication user connection successful after creation"
    else
        echo "✗ Still cannot connect as replication user"
        echo "Checking pg_hba.conf rules..."
        export PGPASSWORD=postgres
        psql -h db_master -p 5432 -U postgres -d postgres -c "SELECT * FROM pg_hba_file_rules WHERE database LIKE '%replication%' OR database LIKE '%all%';"
        exit 1
    fi
fi


echo "Testing pg_basebackup..."
export PGPASSWORD=replicator_password

if pg_basebackup -h db_master -p 5432 -U replicator -D /tmp/test_backup -v -P -W 2>&1; then
    echo "✓ Base backup test successful"
    rm -rf /tmp/test_backup
else
    echo "✗ Base backup test failed"
    echo "This indicates a pg_hba.conf issue"
    exit 1
fi

echo "=== Replication setup completed successfully ==="