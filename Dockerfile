FROM python:3.14-slim

WORKDIR /ecommerce

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY pyproject.toml uv.lock ./

RUN pip install --no-cache-dir uv \
    && uv sync --locked --no-dev

COPY . .

EXPOSE 8000

COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]

CMD ["uv", "run", "uvicorn", "sandbox.asgi:application", "--host", "0.0.0.0", "--port", "8000"]
