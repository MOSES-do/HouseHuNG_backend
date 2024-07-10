-- prepares a MySQL server for the project

CREATE DATABASE IF NOT EXISTS housing_db;
CREATE USER IF NOT EXISTS 'housing_dev'@'localhost' IDENTIFIED BY 'housing_pwd';
GRANT ALL PRIVILEGES ON `housing_db`.* TO 'housing_dev'@'localhost';
GRANT SELECT ON `performance_schema`.* TO 'housing_dev'@'localhost';
FLUSH PRIVILEGES;
