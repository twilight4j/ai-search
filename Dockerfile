FROM python:3.11-slim

RUN pip install --no-cache-dir poetry

WORKDIR /app
COPY pyproject.toml poetry.lock /app/

RUN poetry install --no-root

COPY . /app

CMD ["poetry", "run", "python", "main.py"]