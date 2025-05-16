#!/bin/bash

echo "Waiting for PostgreSQL master to be ready..."
until pg_isready -h db_master -p 5432 -U insurance; do
  sleep 2
done

echo "Waiting for PostgreSQL slave to be ready..."
until pg_isready -h db_slave -p 5432 -U insurance; do
  sleep 2
done

echo "Creating replication user on master..."
psql -h db_master -p 5432 -U insurance -d insurance -c "
CREATE USER replicator WITH REPLICATION ENCRYPTED PASSWORD 'replicator_password';
"

echo "Configuring pg_hba.conf on master..."
psql -h db_master -p 5432 -U insurance -d insurance -c "ALTER SYSTEM SET listen_addresses TO '*';"
psql -h db_master -p 5432 -U insurance -d insurance -c "ALTER SYSTEM SET wal_level TO 'replica';"
psql -h db_master -p 5432 -U insurance -d insurance -c "ALTER SYSTEM SET max_wal_senders TO 10;"
psql -h db_master -p 5432 -U insurance -d insurance -c "ALTER SYSTEM SET max_replication_slots TO 10;"
psql -h db_master -p 5432 -U insurance -d insurance -c "ALTER SYSTEM SET wal_keep_size TO '1GB';"
psql -h db_master -p 5432 -U insurance -d insurance -c "SELECT pg_reload_conf();"

echo "Restarting master..."
pg_ctl -D /var/lib/postgresql/data -m fast -w restart

echo "Waiting for master to be available again..."
until pg_isready -h db_master -p 5432 -U insurance; do
  sleep 2
done

echo "Stopping slave..."
pg_ctl -D /var/lib/postgresql/data -m fast -w stop

echo "Cleaning slave data directory..."
rm -rf /var/lib/postgresql/data/*

echo "Creating base backup from master..."
pg_basebackup -h db_master -p 5432 -U replicator -D /tmp/backup -Fp -Xs -P -R

echo "Copying backup to slave..."
docker cp insurance-postgres-master:/tmp/backup/. insurance-postgres-slave:/var/lib/postgresql/data/

echo "Setting proper permissions on slave data..."
chown -R postgres:postgres /var/lib/postgresql/data
chmod 700 /var/lib/postgresql/data

echo "Creating standby.signal on slave..."
touch /var/lib/postgresql/data/standby.signal

echo "Starting slave..."
pg_ctl -D /var/lib/postgresql/data -w start

echo "Checking replication status..."
sleep 5
psql -h db_master -p 5432 -U insurance -d insurance -c "
SELECT * FROM pg_stat_replication;
"

echo "Replication setup complete!"