# FastAPI Example Project

This code is presented as a prototype, based on the refactoring of a working solution. With no integrity guarantee sufficient to run this service.

# Key Features

## Global db session ContextVar

> The session (AsyncSession) object provided by db.session is based on the Python3.7+ ContextVar. This means that each session is linked to the individual request context in which it was created.

Thanks to [h0rn3t](https://github.com/h0rn3t/fastapi-async-sqlalchemy) for implementing fastapi-middleware, which really avoids db-deadlocks during intensive DML queries to the database.

Additional links:

- [SQLAlchemy Dependency vs. Middleware vs. scoped_session](https://github.com/tiangolo/fastapi/issues/726)
- [Using a DB dependency in FastAPI without having to pass it through a function tree](https://github.com/tiangolo/fastapi/issues/2894)
- [Db connection management - performances](https://github.com/tiangolo/full-stack-fastapi-postgresql/issues/290)


## Advanced Filter & Sort parameters

Details: `app/api/dependencies/sort`, `app/api/dependencies/filters.py`

It is possible to describe filtering and sorting parameters and logical operators in queries with simple syntax.

The values of the query parameters filter, sort are transmitted in URL-encoded string format.

### Sort examples

```
{"property": "created","direction": "desc"}:

GET service-url/endpoint/?sort=%7B%22property%22%3A%20%22created%22,%22direction%22%3A%20%22desc%22%7D

[
    {"property": "account","direction": "asc"},
    {"property": "created","direction": "desc"}
]:

GET service-url/endpoint/?sort=%5B%7B%22property%22%3A%20%22account%22,%22direction%22%3A%20%22asc%22%7D,%7B%22property%22%3A%20%22created%22,%22direction%22%3A%20%22desc%22%7D%5D
```

### Filter examples

```
[
    {"property": "modified","operator": ">=", "value": "2022-08-01"},
    {"property": "modified","operator": "<", "value": "2022-08-06"}
]:

GET service-url/endpoint/?filter=%5B%7B%22property%22%3A%20%22modified%22,%22operator%22%3A%20%22%3E%3D%22,%20%22value%22%3A%20%222022-08-01%22%7D,%7B%22property%22%3A%20%22modified%22,%22operator%22%3A%20%22%3C%22,%20%22value%22%3A%20%222022-08-06%22%7D%5D

{"property":"amount","operator":"=","value":119.8}

GET service-url/endpoint/?filter=%7B%22property%22%3A%22amount%22,%22operator%22%3A%22%3D%22,%22value%22%3A119.8%7D
```

### Run Service

```shell
# Development server
export DEBUG=True

uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1  --log-config loggers-debug.json

# Production server
export DEBUG=False (default)

gunicorn app.main:app
```
