FROM python:3.11.13-slim

WORKDIR /app

COPY ./poetry.lock /app
COPY ./pyproject.toml /app

RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false 

RUN poetry install --no-root

COPY . /app

EXPOSE 8000

CMD ["fastapi", "run", "main.py", "--host", "0.0.0.0", "--port", "8000"]