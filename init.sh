#!/bin/bash

# Monte Carlo Investment Calculator - Initialization Script
# Полная настройка и запуск приложения

echo "🚀 Инициализация Monte Carlo Investment Calculator..."
echo "=================================================="

# Проверка Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен. Пожалуйста, установите Docker."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose не установлен. Пожалуйста, установите Docker Compose."
    exit 1
fi

echo "✅ Docker и Docker Compose найдены"

# Остановка и удаление существующих контейнеров
echo "🧹 Очистка существующих контейнеров..."
docker-compose down --remove-orphans

# Сборка и запуск
echo "🏗️ Сборка и запуск приложения..."
docker-compose up -d --build

# Ожидание запуска
echo "⏳ Ожидание запуска сервисов..."
sleep 10

# Проверка статуса
echo "🔍 Проверка статуса сервисов..."
docker-compose ps

# Тест доступности
echo "🌐 Проверка доступности приложения..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost:5001 | grep -q "200"; then
    echo "✅ Приложение успешно запущено!"
    echo ""
    echo "📱 Откройте в браузере: http://localhost:5001"
    echo ""
    echo "🎯 Возможности:"
    echo "   - Monte Carlo симуляция (1,000 - 50,000 итераций)"
    echo "   - Реалистичные диапазоны доходности (-50% до +100%)"
    echo "   - Готовые инвестиционные стратегии"
    echo "   - Учет инфляции и налогов"
    echo "   - Интерактивные графики"
    echo ""
    echo "🛑 Для остановки: docker-compose down"
    echo "📋 Логи: docker-compose logs web"
else
    echo "❌ Не удалось запустить приложение"
    echo "📋 Проверьте логи: docker-compose logs web"
    exit 1
fi

echo "🎉 Инициализация завершена!"