FROM postgres:latest

ENV POSTGRES_PASSWORD password

EXPOSE 5432

COPY init.sql /docker-entrypoint-initdb.d/
