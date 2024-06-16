#!/bin/sh

# Exit immediately if a command exits with a non-zero status
set -e
# Установка pip, если не установлен (на Windows)
python -m ensurepip --upgrade

# Установка pip, если не установлен (на macOS/Linux)
# python3 -m ensurepip --upgrade

# Создание виртуального окружения
# На Windows
python -m venv venv --prompt "venv" --python=python3.10

# На macOS/Linux
# python3 -m venv venv --prompt "venv" --python=python3.10

# Активация виртуального окружения
# На Windows
venv\Scripts\activate

# На macOS/Linux
# source venv/bin/activate

# Установка зависимостей
pip install -r ./metro_assist/requirements.txt
exec "$@"
