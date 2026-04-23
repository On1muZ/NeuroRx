#!/bin/bash

BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🌐 Запуск туннелей localtunnel...${NC}"
echo "Подождите, пока генерируются ссылки."

# Функция для завершения при нажатии Ctrl+C
trap "kill 0" EXIT

# Запуск туннеля для бэкенда
npx localtunnel --port 8000 &

# Запуск туннеля для фронтенда
npx localtunnel --port 5173 &

wait
