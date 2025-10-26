# 🚀 Быстрый старт с Docker

## Вариант 1: Автоматический запуск (проще всего)

```bash
# 1. Создайте .env файл
cp env.example .env

# 2. Добавьте токен бота в .env
# Отредактируйте .env файл:
nano .env
# Добавьте: TOKEN=your_bot_token_here

# 3. Запустите бота
./start.sh

# Следуйте инструкциям на экране
```

## Вариант 2: Ручной запуск

### Шаг 1: Создайте .env файл

```bash
cp env.example .env
```

### Шаг 2: Добавьте токен

Отредактируйте `.env` и добавьте:
```env
TOKEN=your_telegram_bot_token_here
```

Получите токен у [@BotFather](https://t.me/BotFather)

### Шаг 3: Запустите бота

```bash
# Разработка (SQLite + Redis)
docker-compose -f docker-compose.dev.yml up -d

# Или продакшен (PostgreSQL + Redis)
docker-compose up -d
```

### Шаг 4: Проверьте логи

```bash
docker-compose logs -f bot
```

## Проверка работы

1. Найдите бота в Telegram
2. Отправьте `/start`
3. Попробуйте задать вопрос: "Объясни мне дроби"

## Остановка

```bash
./stop.sh

# Или
docker-compose down
```

## Управление

```bash
# Логи
docker-compose logs -f bot

# Перезапуск
docker-compose restart bot

# Статус
docker-compose ps

# Зайти в контейнер
docker-compose exec bot bash
```

## Что включено в Docker Compose?

- 🤖 **Бот** - Telegram бот Ayana
- 🗄️ **PostgreSQL** - База данных (опционально)
- 💾 **Redis** - Кэш контекста диалогов
- 📡 **API** - REST API сервер (опционально)

## Порты

- Redis: `localhost:6379`
- PostgreSQL: `localhost:5432`
- API: `localhost:8000` (если включен)

## Важные команды

```bash
# Инициализация БД вручную
docker-compose exec bot python init_db.py

# Проверка Redis
docker-compose exec redis redis-cli ping

# Проверка PostgreSQL
docker-compose exec postgres psql -U ayana_user -d ayana_db -c "SELECT 1"
```

## Проблемы?

### Бот не отвечает

```bash
# Проверьте логи
docker-compose logs bot

# Проверьте переменные окружения
docker-compose config
```

### Токен не установлен

Добавьте токен в `.env`:
```bash
echo "TOKEN=your_token" >> .env
docker-compose restart bot
```

### Порты заняты

Измените порты в `docker-compose.yml`

## Опционально: Запуск с API

```bash
docker-compose --profile api up -d
```

API будет доступен на: http://localhost:8000
Документация: http://localhost:8000/docs

---

**Готово! Бот запущен! 🎉**

