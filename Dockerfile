# pull official base image
FROM python:3.11-alpine as base

ENV PYTHONFAULTHANDLER=1 \
  PYTHONHASHSEED=random \
  PYTHONUNBUFFERED=1

WORKDIR /app

FROM base AS builder

ENV PIP_DEFAULT_TIMEOUT=100 \
  PIP_DISABLE_PIP_VERSION_CHECK=1 \
  PIP_NO_CACHE_DIR=1 \
  POETRY_VERSION=1.6.0

RUN apk add --no-cache build-base postgresql-libs \
  && apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev libgomp \
  && pip install "poetry==${POETRY_VERSION}" \
  && python -m venv /venv

COPY pyproject.toml poetry.lock ./
RUN poetry export -f requirements.txt | /venv/bin/pip install -r /dev/stdin

COPY . .
RUN poetry build && /venv/bin/pip install dist/*.whl

FROM base as artifacts

WORKDIR /app

RUN apk add --no-cache libffi libpq
COPY --from=builder /venv /venv
# COPY --from=builder /app/resource /app/resource

ENV VIRTUAL_ENV=/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"