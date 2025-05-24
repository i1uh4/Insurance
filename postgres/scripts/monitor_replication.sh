#!/bin/bash

set -e

echo "=== Starting Replication Monitor ==="


check_replication_status() {
    echo "--- Replication Status Check $(date) ---"
    
    
    echo "Master replication status:"
    psql -h db_master -p 5432 -U insurance -d insurance -c "
        SELECT 
            application_name,
            client_addr,
            state,
            sent_lsn,
            write_lsn,
            flush_lsn,
            replay_lsn,
            write_lag,
            flush_lag,
            replay_lag,
            sync_state
        FROM pg_stat_replication;
    " 2>/dev/null || echo "Failed to get master replication status"
    
    
    echo "Replication slots:"
    psql -h db_master -p 5432 -U insurance -d insurance -c "
        SELECT 
            slot_name,
            slot_type,
            database,
            active,
            restart_lsn,
            confirmed_flush_lsn
        FROM pg_replication_slots;
    " 2>/dev/null || echo "Failed to get replication slots status"
    
    
    echo "Replica status:"
    psql -h db_slave -p 5432 -U insurance -d insurance -c "
        SELECT 
            pg_is_in_recovery() as is_replica,
            CASE 
                WHEN pg_is_in_recovery() THEN pg_last_wal_receive_lsn()
                ELSE NULL 
            END as last_received_lsn,
            CASE 
                WHEN pg_is_in_recovery() THEN pg_last_wal_replay_lsn()
                ELSE NULL 
            END as last_replayed_lsn;
    " 2>/dev/null || echo "Failed to get replica status"
    
    echo "--- End Status Check ---"
    echo ""
}


check_replication_lag() {
    echo "--- Replication Lag Check $(date) ---"
    
    
    MASTER_LSN=$(psql -h db_master -p 5432 -U insurance -d insurance -t -c "SELECT pg_current_wal_lsn();" 2>/dev/null | tr -d ' ')
    REPLICA_LSN=$(psql -h db_slave -p 5432 -U insurance -d insurance -t -c "SELECT pg_last_wal_replay_lsn();" 2>/dev/null | tr -d ' ')
    
    if [ -n "$MASTER_LSN" ] && [ -n "$REPLICA_LSN" ]; then
        LAG_BYTES=$(psql -h db_master -p 5432 -U insurance -d insurance -t -c "SELECT pg_wal_lsn_diff('$MASTER_LSN', '$REPLICA_LSN');" 2>/dev/null | tr -d ' ')
        echo "Replication lag: $LAG_BYTES bytes"
        
        
        if [ "$LAG_BYTES" -gt 104857600 ]; then
            echo "WARNING: Replication lag is high: $LAG_BYTES bytes"
        fi
    else
        echo "Unable to calculate replication lag"
    fi
    
    echo "--- End Lag Check ---"
    echo ""
}


test_replication() {
    echo "--- Testing Replication $(date) ---"
    
    
    TEST_VALUE=$(date +%s)
    psql -h db_master -p 5432 -U insurance -d insurance -c "
        CREATE TABLE IF NOT EXISTS replication_test (
            id SERIAL PRIMARY KEY,
            test_value TEXT,
            created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
        );
        INSERT INTO replication_test (test_value) VALUES ('test_$TEST_VALUE');
    " 2>/dev/null || {
        echo "Failed to insert test data on master"
        return 1
    }
    
    
    sleep 5
    
    
    REPLICA_VALUE=$(psql -h db_slave -p 5432 -U insurance -d insurance -t -c "
        SELECT test_value FROM replication_test WHERE test_value = 'test_$TEST_VALUE' LIMIT 1;
    " 2>/dev/null | tr -d ' ')
    
    if [ "$REPLICA_VALUE" = "test_$TEST_VALUE" ]; then
        echo "✓ Replication test PASSED - Data successfully replicated"
    else
        echo "✗ Replication test FAILED - Data not found on replica"
    fi
    
    
    psql -h db_master -p 5432 -U insurance -d insurance -c "
        DELETE FROM replication_test WHERE test_value = 'test_$TEST_VALUE';
    " 2>/dev/null || echo "Failed to cleanup test data"
    
    echo "--- End Replication Test ---"
    echo ""
}


echo "Waiting for databases to be ready..."
while ! pg_isready -h db_master -p 5432 -U insurance >/dev/null 2>&1; do
    sleep 5
done

while ! pg_isready -h db_slave -p 5432 -U insurance >/dev/null 2>&1; do
    sleep 5
done

echo "Both databases are ready, starting monitoring..."


COUNTER=0
while true; do
    check_replication_status
    check_replication_lag
    
    
    if [ $((COUNTER % 10)) -eq 0 ]; then
        test_replication
    fi
    
    COUNTER=$((COUNTER + 1))
    sleep 30
done