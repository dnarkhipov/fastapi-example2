# Manage migrations with [Alembic](https://alembic.sqlalchemy.org/en/latest/index.html#)

## Create a Migration Script

```shell
alembic revision -m "Init"
```

## Auto Generating Migrations

```shell
alembic revision --autogenerate -m "Init"
```

## Running migration

```shell
alembic upgrade head
```

## Getting Information

```shell
alembic current
```

## Downgrade back to the beginning

```shell
alembic downgrade base
```
