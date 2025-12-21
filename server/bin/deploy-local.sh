#!/bin/bash

set -euo pipefail # 에러 발생 시 즉시 종료

# python venv 경로를 PATH로 저장
VENV_DIR="/opt/python-venv/venv"
export PATH="$VENV_DIR/bin:$PATH"


alembic -c /app/model/alembic.ini upgrade head
runserver