-- Create a new user with read-only access
CREATE USER 'readonly_user'@'%' IDENTIFIED BY 'readonly_password';

-- Grant SELECT permission on the testdb database
GRANT SELECT ON testdb.* TO 'readonly_user'@'%';

-- Apply changes
FLUSH PRIVILEGES;
