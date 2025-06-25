FROM python:3.13-slim-bookworm

COPY --from=ghcr.io/astral-sh/uv:0.7.8 /uv /uvx /bin/

ADD . /app

WORKDIR /app

RUN uv sync --locked

CMD [ "uv", "run", "/app/main.py" ]