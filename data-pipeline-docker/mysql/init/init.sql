CREATE DATABASE IF NOT EXISTS test;
CREATE DATABASE IF NOT EXISTS ETL;
CREATE USER IF NOT EXISTS 'airflow'@'%' IDENTIFIED BY 'airflow';
GRANT ALL PRIVILEGES ON airflow_db.* TO 'airflow'@'%';
GRANT ALL PRIVILEGES ON test.* TO 'airflow'@'%';
-- Create Prometheus exporter user
CREATE USER IF NOT EXISTS 'exporter'@'%' IDENTIFIED BY 'exporter_password';
-- Grant read-only access and performance schema access
GRANT PROCESS, REPLICATION CLIENT, SELECT ON *.* TO 'exporter'@'%';
-- Optional: Ensure access to performance_schema
GRANT SELECT ON performance_schema.* TO 'exporter'@'%';
FLUSH PRIVILEGES;