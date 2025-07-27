// init-mongo.js

db = db.getSiblingDB('admin');

// Create root user
db.createUser({
  user: 'root',
  pwd: 'pass',
  roles: [{ role: 'root', db: 'admin' }]
});

// Create exporter user for Prometheus exporter
db.createUser({
  user: 'exporter',
  pwd: 'exporter_password',
  roles: [
    { role: 'readAnyDatabase', db: 'admin' },
    { role: 'clusterMonitor', db: 'admin' },
    { role: 'read', db: 'local' },
    { role: 'read', db: 'admin' }
  ]
});

// ETL Database Initialization 
etlDb = db.getSiblingDB('ETL');