FROM python:3.12 AS base

WORKDIR /code

COPY . .

FROM base AS dev

RUN pip install -e .

FROM base AS deploy

RUN pip install .
