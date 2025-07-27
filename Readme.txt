========================= Environment ==================================

Windows machine with 8GB RAM,Windows Docker Desktop Application installed.
It's lightweight approach to demonstrate the Fullstack docker
It has mysql + mongodb + kafka + zookeeper + airflow + airflow-scheduler
also it has grafana + prometheus + mysql-exporter + mongodb-exporter
In my setup mysql airflow_db is being used for airflow backend database.
mysql ETL DB is being used for ETL work purpose
This is done to build lightweight demo setup, but in production 
separate database instance should be used for airflow.

========================== Docker creation =======================

Project Path:"D:\Data Engineering Course\Final_Capstone_project\data-pipeline-docker"

First airflow custom image build creation with all python dependencies
using Dockerfile and requirements.txt
D:\Data Engineering Course\Final_Capstone_project\data-pipeline-docker>docker build -t airflow-custom:latest .

Then 
D:\Data Engineering Course\Final_Capstone_project\data-pipeline-docker>docker-compose up -d --build

D:\Data Engineering Course\Final_Capstone_project\data-pipeline-docker>docker images
REPOSITORY                           TAG          IMAGE ID       CREATED         SIZE
airflow-custom                       latest       e04fe03fc696   25 hours ago    2.03GB
mongo                                6.0          e6ea23317a13   8 days ago      1.05GB
prom/prometheus                      latest       63805ebb8d2b   12 days ago     440MB
grafana/grafana                      latest       b5b59bfc7561   6 weeks ago     897MB
mysql                                8.0-oracle   63823b8e2cbe   3 months ago    1.06GB
prom/mysqld-exporter                 latest       20b5b23a98ce   5 months ago    34.9MB
quay.io/prometheus/mysqld-exporter   latest       20b5b23a98ce   5 months ago    34.9MB
confluentinc/cp-kafka                7.6.0        24cdd3a7fa89   17 months ago   1.31GB
confluentinc/cp-zookeeper            7.6.0        9babd1c0beaf   17 months ago   1.31GB
percona/mongodb_exporter             0.40.0       d66daa6aff05   20 months ago   21MB

D:\Data Engineering Course\Final_Capstone_project\data-pipeline-docker>docker ps
NAMES                                           STATUS       PORTS                                             
data-pipeline-docker-airflow-scheduler-1        Up 1 hours   8080/tcp                                          
data-pipeline-docker-airflow-1                  Up 1 hours   0.0.0.0:8081->8080/tcp, [::]:8081->8080/tcp       
data-pipeline-docker-kafka-1                    Up 1 hours   0.0.0.0:9092->9092/tcp, [::]:9092->9092/tcp       
data-pipeline-docker-mongodb-exporter-1         Up 1 hours   0.0.0.0:9216->9216/tcp, [::]:9216->9216/tcp       
data-pipeline-docker-mysql-exporter-1           Up 1 hours   0.0.0.0:9104->9104/tcp, [::]:9104->9104/tcp       
data-pipeline-docker-grafana-1                  Up 1 hours   0.0.0.0:3000->3000/tcp, [::]:3000->3000/tcp       
data-pipeline-docker-mongodb-1                  Up 1 hours   0.0.0.0:27016->27017/tcp, [::]:27016->27017/tcp   
data-pipeline-docker-mysql-1                    Up 1 hours   0.0.0.0:3305->3306/tcp, [::]:3305->3306/tcp       
data-pipeline-docker-prometheus-1               Up 1 hours   0.0.0.0:9090->9090/tcp, [::]:9090->9090/tcp       
data-pipeline-docker-zookeeper-1                Up 1 hours   0.0.0.0:2181->2181/tcp, [::]:2181->2181/tcp       

============================== Certain Checks on Containers =====================

==========kafka testing==================
docker ps
docker exec -it data-pipeline-docker-kafka-1 bash
/usr/bin/kafka-topics --bootstrap-server localhost:9092 --list
docker exec -it data-pipeline-docker-airflow-1 getent hosts kafka
==========mongodb testing=================
docker exec -it data-pipeline-docker-mongodb-1 mongosh
show dbs
and later
docker exec -it data-pipeline-docker-airflow-1 bash
python -c "from pymongo import MongoClient; MongoClient('mongodb://mongodb:27017').admin.command('ping'); print('MongoDB is reachable')"
airflow@dc25fdc6c6fb:/opt/airflow$ python -c "from pymongo import MongoClient; MongoClient('mongodb://mongodb:27017').admin.command('ping'); print('MongoDB is reachable')"
MongoDB is reachable
=============mysql testing===================
docker exec -it data-pipeline-docker-mysql-1 mysql -u root -p
and later
docker exec -it data-pipeline-docker-airflow-1 bash
python -c "import pymysql; conn = pymysql.connect(host='mysql', user='airflow', password='airflow', database='airflow_db'); print('MySQL is reachable'); conn.close()"
=============network inspection=============
docker network inspect data-pipeline-docker_monitoring

then open browser and check airflow
http://localhost:8081/   admin/admin
then open browser and check grafana
http://localhost:3000/   admin/admin
then open browser and check promethues
http://localhost:9090/    direct login

we have init.sql and init.js for initial user/db creation but incase that didn't work
or you have to rebuild volume/containers from crash or any such adverse scenario
below are certain useful commands but certainly not exhaustive

docker exec -it data-pipeline-docker-airflow-1 airflow users create ^
  --username admin ^
  --firstname Admin ^
  --lastname User ^
  --role Admin ^
  --email admin@example.com ^
  --password admin

db.createUser({
  user: "root",
  pwd: "pass",
  roles: [ { role: "root", db: "admin" } ]
}) 
db.createUser({
  user: "exporter",
  pwd: "exporterpassword",
  roles: [
    { role: "clusterMonitor", db: "admin" },
    { role: "read", db: "local" },
    { role: "read", db: "admin" },
    { role: "readAnyDatabase", db: "admin" }
  ]
})

docker exec -it data-pipeline-docker-mysql-1 mysql -u root -p
SELECT user, host FROM mysql.user WHERE user = 'airflow';
SHOW GRANTS FOR 'airflow'@'%';
CREATE DATABASE IF NOT EXISTS airflow_db;
CREATE DATABASE IF NOT EXISTS test;
CREATE DATABASE IF NOT EXISTS ETL;
CREATE USER IF NOT EXISTS 'airflow'@'%' IDENTIFIED BY 'airflow';
GRANT ALL PRIVILEGES ON airflow_db.* TO 'airflow'@'%';
FLUSH PRIVILEGES;

==========================prometheus inspection=============
If all .yml file setup and user config is correct then in prometheus status target health
below 3 services should be up and green
http://mongodb-exporter:9216/metrics
instance="mongodb-exporter:9216"
job="mongodb"
http://mysql-exporter:9104/metrics
instance="mysql-exporter:9104"
job="mysql"
http://localhost:9090/metrics
instance="localhost:9090"
job="prometheus"

====================== Grafana dashboard setup =========================

1. MySQL Overview Dashboard
Dashboard Name: MySQL Overview
Dashboard ID: 7362
Import URL:
https://grafana.com/grafana/dashboards/7362
Includes MySQL metrics like connections, queries/sec, buffer usage, 
slow queries (requires MySQL exporter + Prometheus)

2. MongoDB Metrics Dashboard
Dashboard Name: MongoDB Overview
Dashboard ID: 2583
Import URL:
https://grafana.com/grafana/dashboards/2583
Includes MongoDB memory, ops/sec, connections, document stats 
(requires MongoDB exporter + Prometheus)

Ecommerce_Analytics Dashboard I have self-created

========================== ETL DAG Flow Planning ==================

=================Task1=================
mongodb inventory collection data will be fetched 
and will load in inventory table in mysql ETL database
=================Task2=================
delivery.json,orders.json will be in below path
D:\Data Engineering Course\Final_Capstone_project\data-pipeline-docker\kafka\kafka_input
It will pick them and process them via kafka producer-consumer
and will load them in delivery,orders table in mysql ETL database
=================Task3=================
6th July 2025 single day order, delivery info
will be combined in masterdata where combined last 1 month data is stored.
It will also update last_order_qty,remain_inventory,Last_updatetime in inventory table in mysql
Basically the order effect on inventory will be captured
=================Task4=================
masterdata has sameday_order_status,sameday_delivery_status column which is daily info.
For 6th July 2025 single day it will update 
final_order_status,final_delivery_status,ordercycle_indicator column in masterdata table
Basically it will detect order cycle which order are same day delivery, 
which are beyond same day, which are cancelled etc.
For example 5th July 2025 few orders will be finally completed on 6th July 2025.

sysrundate is the common processing date column across the mysql masterdata, orders, delivery table.
Inventory is latest instance only for simplification.
We can say masterdata is Fact table, orders, delivery, inventory  is dimension table


========================== ETL Database Table, sql/python script, datafiles ==================

delivery.json,orders.json contain 6th July 2025 single day data for ETL demotest
delivery_fulltable.json, orders_fulltable.json, inventory_fulltable.json
masterdata_fulltable.json contains data for entire table, business duration:6th June-6th July 1 month data
mysql_tablecreation_scripts.sql is for creating tables in mysql ETL database
load_all_json_to_mysql.py script is to load 1 month data using multiple files in mysql tables
mongodb_inventory.csv is for initial inventory collection data in mongodb
load_all_csv_to_mongodb.py script is to load inventory data in mongodb ETL database

Analytics_related.sql -- it has Grafana Ecommerce_Analytics dashboard related various sqls

Sampledata.xlsx -- it has masterdata and inventory data in 1st 2 tab.
We can explain a business person by showing this data

============================== ETL Test procedure Flow =================
===============data cleanup scripts before demo ETL test==================
delete from delivery
where sysrundate ='2025-07-06';
delete from orders
where sysrundate ='2025-07-06';
delete from inventory;
delete from masterdata
where sysrundate ='2025-07-06';
=================data check scripts after ETL run========================
select * from delivery
where sysrundate ='2025-07-06';
select *  from orders
where sysrundate ='2025-07-06';
select *  from inventory;
select *  from masterdata
where sysrundate ='2025-07-06';
