#!/bin/bash

set -e

echo "=== Starting Insurance Recommendation System with PostgreSQL Replication ==="


check_compose_status() {
    echo "Checking Docker Compose status..."
    docker compose ps
    echo ""
}


check_logs() {
    local service=$1
    local lines=${2:-50}
    echo "=== Logs for $service (last $lines lines) ==="
    docker compose logs --tail=$lines "$service" || echo "Failed to get logs for $service"
    echo ""
}


check_database_connection() {
    local host=$1
    local port=$2
    local description=$3
    
    echo "Testing connection to $description ($host:$port)..."
    if docker compose exec -T db_master pg_isready -h "$host" -p "$port" -U insurance; then
        echo "✓ $description is accessible"
    else
        echo "✗ $description is not accessible"
    fi
}


check_replication() {
    echo "=== Checking Replication Status ==="
    
    echo "Master replication status:"
    docker compose exec -T db_master psql -U insurance -d insurance -c "
        SELECT 
            application_name,
            client_addr,
            state,
            sync_state
        FROM pg_stat_replication;
    " || echo "Failed to check master replication status"
    
    echo "Slave recovery status:"
    docker compose exec -T db_slave psql -U insurance -d insurance -c "
        SELECT 
            pg_is_in_recovery() as is_replica,
            pg_last_wal_receive_lsn() as last_received_lsn,
            pg_last_wal_replay_lsn() as last_replicated_lsn;
    " || echo "Failed to check slave recovery status"
    
    echo ""
}


test_data_replication() {
    echo "=== Testing Data Replication ==="
    
    local test_value=$(date +%s)
    
    echo "Inserting test data on master..."
    docker compose exec -T db_master psql -U insurance -d insurance -c "
        CREATE TABLE IF NOT EXISTS replication_test (
            id SERIAL PRIMARY KEY,
            test_value TEXT,
            created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
        );
        INSERT INTO replication_test (test_value) VALUES ('test_$test_value');
    " || {
        echo "Failed to insert test data"
        return 1
    }
    
    echo "Waiting for replication..."
    sleep 5
    
    echo "Checking test data on slave..."
    local result=$(docker compose exec -T db_slave psql -U insurance -d insurance -t -c "
        SELECT COUNT(*) FROM replication_test WHERE test_value = 'test_$test_value';
    " | tr -d ' \n\r')
    
    if [ "$result" = "1" ]; then
        echo "✓ Data replication test PASSED"
    else
        echo "✗ Data replication test FAILED"
    fi
    
    
    docker compose exec -T db_master psql -U insurance -d insurance -c "
        DELETE FROM replication_test WHERE test_value = 'test_$test_value';
    " || echo "Failed to cleanup test data"
    
    echo ""
}


echo "Setting execute permissions for scripts..."
chmod +x postgres/scripts/*.sh


echo "Stopping existing containers..."
docker compose down -v || true


echo "Creating WAL archive directories..."
mkdir -p ./postgres/wal_archive


echo "Starting the system..."
echo "This may take several minutes for the first time..."


docker compose up -d

echo "Waiting for services to start..."
sleep 10


check_compose_status


echo "Waiting for master database to be ready..."
timeout=300
counter=0
while [ $counter -lt $timeout ]; do
    if docker compose exec -T db_master pg_isready -U insurance >/dev/null 2>&1; then
        echo "✓ Master database is ready"
        break
    fi
    sleep 5
    counter=$((counter + 5))
    echo "Waiting... ($counter/$timeout seconds)"
done

if [ $counter -ge $timeout ]; then
    echo "✗ Master database failed to start within $timeout seconds"
    check_logs db_master
    exit 1
fi

echo "Waiting for slave database to be ready..."
counter=0
while [ $counter -lt $timeout ]; do
    if docker compose exec -T db_slave pg_isready -U insurance >/dev/null 2>&1; then
        echo "✓ Slave database is ready"
        break
    fi
    sleep 5
    counter=$((counter + 5))
    echo "Waiting... ($counter/$timeout seconds)"
done

if [ $counter -ge $timeout ]; then
    echo "✗ Slave database failed to start within $timeout seconds"
    check_logs db_slave
    exit 1
fi


check_database_connection "localhost" "5432" "Master Database"
check_database_connection "localhost" "5433" "Slave Database"


sleep 10
check_replication


test_data_replication


echo "=== Checking Database Schema ==="
echo "Tables in master database:"
docker compose exec -T db_master psql -U insurance -d insurance -c "\dt" || echo "Failed to list tables in master"

echo "Tables in slave database:"
docker compose exec -T db_slave psql -U insurance -d insurance -c "\dt" || echo "Failed to list tables in slave"


echo "=== Checking Application Services ==="
echo "Waiting for application services..."
sleep 30

if curl -f http://localhost:8000/health >/dev/null 2>&1; then
    echo "✓ Main API service is responding"
else
    echo "⚠ Main API service is not responding yet (this may be normal during startup)"
fi

if curl -f http://localhost:8001/health >/dev/null 2>&1; then
    echo "✓ Recommendation service is responding"
else
    echo "⚠ Recommendation service is not responding yet (this may be normal during startup)"
fi

echo ""
echo "=== System Startup Complete ==="
echo ""
echo "Services available:"
echo "- Master Database: localhost:5432"
echo "- Slave Database:  localhost:5433"
echo "- Main API:        http://localhost:8000"
echo "- ML API:          http://localhost:8001"
echo ""
echo "To check logs:"
echo "  docker compose logs -f [service_name]"
echo ""
echo "To check replication status:"
echo "  docker compose exec db_master psql -U insurance -d insurance -c 'SELECT * FROM pg_stat_replication;'"
echo ""
echo "To monitor replication continuously:"
echo "  docker compose logs -f replication_monitor"
echo ""


check_compose_status