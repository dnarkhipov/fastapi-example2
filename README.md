# FastAPI Example Project


### Run Service

```shell
# Development server
export DEBUG=True

uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1  --log-config loggers-debug.json

# Production server
export DEBUG=False (default)

gunicorn app.main:app
```
