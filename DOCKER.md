# 🐳 Запуск через Docker

## Быстрый старт

### 1. Создайте .env файл

```bash
cp env.example .env
```

Отредактируйте `.env` и добавьте токен бота:
```env
TOKEN=your_telegram_bot_token_here
```

### 2. Запуск с PostgreSQL (продакшен)

```bash
# Запустить все сервисы
docker-compose up -d

# Посмотреть логи бота
docker-compose logs -f bot

# Остановить
docker-compose down
```

### 3. Запуск с SQLite (разработка)

```bash
# Запустить только бота и Redis (без PostgreSQL)
docker-compose -f docker-compose.dev.yml up -d

# Посмотреть логи
docker-compose -f docker-compose.dev.yml logs -f bot
```

### 4. Запуск с API сервером

```bash
# Запустить бота + API
docker-compose --profile api up -d

# API будет доступен на http://localhost:8000
# Документация: http://localhost:8000/docs
```

## Доступные сервисы

- **Бот:** Работает в `bot` контейнере
- **PostgreSQL:** `localhost:5432`
- **Redis:** `localhost:6379`
- **FastAPI:** `localhost:8000` (если включен профиль api)

## Управление

### Логи

```bash
# Все логи
docker-compose logs -f

# Только бот
docker-compose logs -f bot

# Только база данных
docker-compose logs -f postgres
```

### Перезапуск

```bash
# Перезапустить бота
docker-compose restart bot

# Перезапустить все
docker-compose restart
```

### Остановка

```bash
# Остановить с удалением контейнеров
docker-compose down

# Остановить с удалением контейнеров и volumes (ОСТОРОЖНО!)
docker-compose down -v
```

### Билд образа

```bash
# Пересобрать образ
docker-compose build --no-cache

# Затем запустить
docker-compose up -d
```

## Инициализация БД

БД инициализируется автоматически при первом запуске:

```bash
# Если нужно вручную инициализировать
docker-compose exec bot python init_db.py
```

## Проверка работы

```bash
# Проверить статус
docker-compose ps

# Проверить Redis
docker-compose exec redis redis-cli ping
# Должно вернуть: PONG

# Проверить PostgreSQL
docker-compose exec postgres psql -U ayana_user -d ayana_db -c "SELECT 1;"
```

## Масштабирование

```bash
# Запустить несколько экземпляров бота (если нужно)
docker-compose up -d --scale bot=2
```

## Доступ к базе данных

```bash
# PostgreSQL
docker-compose exec postgres psql -U ayana_user -d ayana_db

# Redis
docker-compose exec redis redis-cli

# Файлы базы данных
docker-compose exec bot ls -la /app
```

## Решение проблем

### Проблема: Бот не запускается

```bash
# Посмотрите логи
docker-compose logs bot

# Проверьте переменные окружения
docker-compose config
```

### Проблема: Токен не установлен

```bash
# Добавьте токен в .env
echo "TOKEN=your_token" >> .env

# Перезапустите бота
docker-compose restart bot
```

### Проблема: Порт занят

Измените порты в `docker-compose.yml`:

```yaml
ports:
  - "5433:5432"  # Вместо 5432:5432
```

### Очистка данных

```bash
# Удалить все данные (БД, Redis)
docker-compose down -v

# Затем перезапустить
docker-compose up -d
```

## Переменные окружения

Создайте `.env` файл:

```env
# Обязательно
TOKEN=your_telegram_bot_token_here

# PostgreSQL (по умолчанию используются значения из docker-compose)
USE_POSTGRES=true
POSTGRES_USER=ayana_user
POSTGRES_PASSWORD=ayana_pass
POSTGRES_SERVER=postgres
POSTGRES_PORT=5432
POSTGRES_DB=ayana_db

# Redis
REDIS_URL=redis://redis:6379/0

# API
API_HOST=0.0.0.0
API_PORT=8000

# Environment
ENVIRONMENT=production
```

## Production деплой

Для production рекомендуется:

1. Использовать PostgreSQL вместо SQLite
2. Настроить регулярные бэкапы БД
3. Использовать Docker secrets для токенов
4. Настроить мониторинг и логирование
5. Использовать reverse proxy для API

Пример с nginx:

```nginx
location /api/ {
    proxy_pass http://ayana-api:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

---

**Готово! Бот запущен в Docker!** 🐳

