CREATE DATABASE red_goat_eyes
    WITH
    ENCODING = 'UTF8'
    TEMPLATE = template0
    CONNECTION LIMIT = -1;



SELECT datname        AS base_de_datos,
       pg_encoding_to_char(encoding) AS codificacion,
       datcollate      AS ordenamiento
FROM   pg_database
WHERE  datname = 'red_goat_eyes';
