#!/bin/bash

# Цвета для вывода
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 Запуск NeuroRx...${NC}"

# 1. Проверка и установка зависимостей бэкенда
echo -e "${GREEN}📦 Настройка Backend (uv)...${NC}"
cd backend
if ! command -v uv &> /dev/null; then
    echo "uv не найден. Устанавливаю..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi
uv sync

# 2. Миграции базы данных
echo -e "${GREEN}🗄️ Применение миграций БД...${NC}"
uv run alembic upgrade head

# 3. Настройка фронтенда
echo -e "${GREEN}📦 Настройка Frontend (npm)...${NC}"
cd ../frontend
npm install

# 4. Запуск приложения
echo -e "${BLUE}✨ Запуск серверов...${NC}"

# Функция для завершения всех фоновых процессов при выходе
trap "kill 0" EXIT

# Запуск бэкенда в фоновом режиме
cd ../backend
uv run python main.py & 

# Запуск фронтенда
cd ../frontend
npm run dev
