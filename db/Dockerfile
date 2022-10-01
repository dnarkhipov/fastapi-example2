# pull official base image
FROM postgres:12.6-alpine

# run create.sql on init
ADD create-db.sh /docker-entrypoint-initdb.d
