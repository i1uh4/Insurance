#!/bin/bash

set -e

echo "=== Starting PostgreSQL Slave Setup ==="

wait_for_master() {
    local max_attempts=60
    local attempt=1

    echo "Waiting for master database to be ready..."
    while [ $attempt -le $max_attempts ]; do
        if pg_isready -h db_master -p 5432 -U insurance >/dev/null 2>&1; then
            echo "Master database is ready!"
            return 0
        fi
        echo "Attempt $attempt/$max_attempts: Master not ready yet..."
        sleep 5
        attempt=$((attempt + 1))
    done

    echo "ERROR: Master database failed to become ready after $max_attempts attempts"
    return 1
}

wait_for_master

if [ -f "$PGDATA/PG_VERSION" ]; then
    echo "Database already initialized, checking if it's a replica..."

    if [ -f "$PGDATA/standby.signal" ]; then
        echo "This is already configured as a replica, starting PostgreSQL..."
        exec gosu postgres postgres -c config_file=/etc/postgresql/postgresql.conf
    else
        echo "Database exists but not configured as replica, reconfiguring..."
        rm -rf "$PGDATA"/*
    fi
fi

echo "Initializing replica from master..."

echo "Creating base backup from master..."
PGPASSWORD="$POSTGRES_REPLICATION_PASSWORD" pg_basebackup \
    -h db_master \
    -p 5432 \
    -U "$POSTGRES_REPLICATION_USER" \
    -D "$PGDATA" \
    -Fp \
    -Xs \
    -P \
    -R \
    -W || {
    echo "ERROR: Failed to create base backup"
    exit 1
}

echo "Setting proper permissions..."
chown -R postgres:postgres "$PGDATA"
chmod 700 "$PGDATA"

echo "Creating standby.signal..."
touch "$PGDATA/standby.signal"

echo "Configuring replication settings..."
cat > "$PGDATA/postgresql.auto.conf" << EOF
primary_conninfo = 'host=db_master port=5432 user=$POSTGRES_REPLICATION_USER password=$POSTGRES_REPLICATION_PASSWORD application_name=replica_slave'
primary_slot_name = 'replica_slot'
restore_command = 'cp /var/lib/postgresql/data/pg_wal/%f %p'
recovery_target_timeline = 'latest'
hot_standby = on
hot_standby_feedback = on
EOF

echo "=== Replica configuration completed ==="

echo "Starting PostgreSQL as replica..."
exec gosu postgres postgres -c config_file=/etc/postgresql/postgresql.conf