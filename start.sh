#!/bin/bash

# Скрипт для быстрого запуска бота

echo "🚀 Запуск Ayana Bot через Docker..."

# Проверка наличия .env файла
if [ ! -f .env ]; then
    echo "📝 Создаю .env файл..."
    cp env.example .env
    echo "⚠️  НЕ ЗАБУДЬТЕ ДОБАВИТЬ ТОКЕН БОТА В .env ФАЙЛ!"
    echo "Отредактируйте .env и добавьте: TOKEN=your_bot_token"
    exit 1
fi

# Проверка наличия токена
if ! grep -q "TOKEN=" .env || grep -q "TOKEN=your" .env || grep -q "TOKEN=$" .env; then
    echo "⚠️  Токен бота не установлен в .env файле!"
    echo "Отредактируйте .env и добавьте: TOKEN=your_bot_token_here"
    exit 1
fi

# Выбор режима запуска
echo ""
echo "Выберите режим запуска:"
echo "1) Разработка (SQLite + Redis)"
echo "2) Продакшен (PostgreSQL + Redis)"
echo "3) С API сервером"
read -p "Ваш выбор [1-3]: " choice

case $choice in
    1)
        echo "📦 Запуск в режиме разработки..."
        docker-compose -f docker-compose.dev.yml up -d
        ;;
    2)
        echo "📦 Запуск в режиме продакшена..."
        docker-compose up -d
        ;;
    3)
        echo "📦 Запуск с API сервером..."
        docker-compose --profile api up -d
        ;;
    *)
        echo "Неверный выбор, запускаю по умолчанию (разработка)"
        docker-compose -f docker-compose.dev.yml up -d
        ;;
esac

echo ""
echo "✅ Бот запущен!"
echo ""
echo "Логи: docker-compose logs -f bot"
echo "Остановка: docker-compose down"
echo ""

