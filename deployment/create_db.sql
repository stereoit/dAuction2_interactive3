CREATE ROLE :user WITH LOGIN PASSWORD ':passwd';
CREATE DATABASE dauction2 OWNER :user;
GRANT ALL PRIVILEGES ON DATABASE dauction2 TO :user;

