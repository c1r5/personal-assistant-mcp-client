FROM python:3.13-slim-bookworm

COPY --from=ghcr.io/astral-sh/uv:0.7.8 /uv /uvx /bin/

WORKDIR /app

COPY ./assistant_agent /app/assistant_agent
COPY ./chatbot/ /app/chatbot/
COPY ./mcp.json /app/
COPY ./main.py /app/
COPY ./uv.lock /app/
COPY ./pyproject.toml /app/

RUN uv sync --locked

CMD [ "uv", "run", "main.py" ]
