#!/bin/bash

alembic upgrade head

uvicorn app.main:app --port=8000 --host=0.0.0.0