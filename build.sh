#!/bin/bash
# Скрипт для быстрой сборки и запуска Docker-контейнера

echo "Начинаем сборку Docker-контейнера..."

# Сборка контейнера
docker-compose build --no-cache

# Запуск сервисов
docker-compose up -d

echo "Контейнеры запущены. Проверить статус можно командой: docker-compose ps"
echo "Логи API сервиса: docker-compose logs -f api"
echo "Логи Frontend сервиса: docker-compose logs -f frontend"