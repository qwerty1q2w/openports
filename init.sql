-- init.sql
CREATE DATABASE IF NOT EXISTS my_port_scanner_db;
CREATE USER IF NOT EXISTS 'myuser'@'%' IDENTIFIED BY 'mypassword';
GRANT ALL PRIVILEGES ON my_port_scanner_db.* TO 'myuser'@'%';
FLUSH PRIVILEGES;
