FROM python:3.14-slim

WORKDIR /ecommerce

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/ecommerce/.venv/bin:$PATH"

COPY pyproject.toml uv.lock ./

RUN pip install --no-cache-dir uv \
    && uv sync --locked --no-dev

COPY . .

EXPOSE 8000

RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]

CMD ["sh", "-c", "uvicorn sandbox.asgi:application --host 0.0.0.0 --port ${PORT:-8000} --log-level debug --access-log"]