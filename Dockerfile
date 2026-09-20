FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:0.12.5 /uv /uvx /bin/

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/app/.venv/bin:$PATH"

RUN groupadd --system teamflow \
    && useradd \
        --system \
        --gid teamflow \
        --create-home \
        teamflow

COPY pyproject.toml uv.lock ./

RUN uv sync \
    --frozen \
    --no-dev

COPY --chown=teamflow:teamflow . .

USER teamflow

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--config", "gunicorn.conf.py"]