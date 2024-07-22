-- creates MySQL server user `user_0d_1` w/ pswd, `user_0d_1_pwd`
-- CREATE USER IF NOT EXISTS 'holberton_user'@'localhost' IDENTIFIED BY 'projectcorrection280hbtn';
-- GRANT REPLICATION CLIENT ON *.* TO 'holberton_user'@'localhost'
GRANT RELOAD ON *.* TO 'holberton_user'@'localhost'
-- permission allows user to check to mysql user table for permissions set for user
-- GRANT SELECT ON mysql.user TO 'holberton_user'@'localhost';
-- GRANT RELOAD ON mysql.user TO 'holberton_user'@'localhost';
