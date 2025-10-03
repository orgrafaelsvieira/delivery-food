FROM python:3.11.13-slim

WORKDIR /app

COPY src/ /app

RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false 

RUN poetry install --no-root

EXPOSE 8000

CMD ["fastapi", "dev"]
