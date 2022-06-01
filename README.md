# Netflix API
Сервис авторизации для онлайн-кинотеатра _Netflix_.

## Сервисы
- Netflix Admin: https://github.com/ReznikovRoman/netflix-admin
- Netflix ETL: https://github.com/ReznikovRoman/netflix-etl
- Netflix Movies API: https://github.com/ReznikovRoman/netflix-movies-api
- Netflix Auth API: https://github.com/ReznikovRoman/netflix-auth-api

## Настройка и запуск
Docker конфигурации содержат контейнеры:
 1. server
 2. redis
 3. db
 4. traefik

Файлы docker-compose:
 1. `docker-compose.yml` - для локальной разработки

Для запуска контейнеров нужно создать файл `.env` в корне проекта.

**Пример `.env`:**

```dotenv
ENV=.env

# Python
PYTHONUNBUFFERED=1

# Netflix Auth API
FLASK_APP=main.py
# Project
NAA_SECRET_KEY=
NAA_SQLALCHEMY_ECHO=1
NAA_PROJECT_BASE_URL=http://api-auth.localhost:8009
NAA_API_V1_STR=/api/v1
NAA_SERVER_NAME=api-auth.localhost:8009
NAA_SERVER_HOSTS=http://api-auth.localhost:8009
NAA_SERVER_PORT=8002
NAA_PROJECT_NAME=netflix-auth
NAA_THROTTLE_KEY_PREFIX=limiter:
NAA_THROTTLE_DEFAULT_LIMITS=50/hour
NAA_THROTTLE_USER_REGISTRATION_LIMITS=5/minute
NAA_DEBUG=1
# auth0
NAA_AUTH0_DOMAIN=
NAA_AUTH0_API_AUDIENCE=
NAA_AUTH0_ISSUER=
# Postgres
NAA_DB_HOST=db
NAA_DB_PORT=5432
NAA_DB_NAME=
NAA_DB_USER=
NAA_DB_PASSWORD=
# Redis
NAA_REDIS_HOST=redis
NAA_REDIS_PORT=6379
NAA_REDIS_THROTTLE_STORAGE_DB=2
NAA_REDIS_DEFAULT_CHARSET=utf-8
NAA_REDIS_DECODE_RESPONSES=1
NAA_REDIS_RETRY_ON_TIMEOUT=1
```

### Запуск проекта:

Локально:
```shell
docker-compose build
docker-compose up
```

## Разработка
Синхронизировать окружение с `requirements.txt` / `requirements.dev.txt` (установит отсутствующие пакеты, удалит лишние, обновит несоответствующие версии):
```shell
make sync-requirements
```

Сгенерировать requirements.\*.txt files (нужно пере-генерировать после изменений в файлах requirements.\*.in):
```shell
make compile-requirements
```

Используем `requirements.local.in` для пакетов, которые нужно только разработчику. Обязательно нужно указывать _constraints files_ (-c ...)

Пример:
```shell
# requirements.local.txt

-c requirements.txt

ipython
```

### Тесты
Запуск тестов (всех, кроме функциональных) с экспортом переменных окружения из `.env` файла:
```shell
export $(echo $(cat .env | sed 's/#.*//g'| xargs) | envsubst) && make test
```

Для функциональных тестов нужно создать файл `.env` в папке ./tests/functional

**Пример `.env`:**
```dotenv
ENV=.env

# Python
PYTHONUNBUFFERED=1

# Netflix Auth API
FLASK_APP=main.py
# Project
NAA_SECRET_KEY=
NAA_SQLALCHEMY_ECHO=1
NAA_PROJECT_BASE_URL=http://api-auth.localhost:8009
NAA_API_V1_STR=/api/v1
NAA_SERVER_NAME=server:8002
NAA_SERVER_HOSTS=http://api-auth.localhost:8009
NAA_SERVER_PORT=8002
NAA_PROJECT_NAME=netflix-auth
NAA_THROTTLE_KEY_PREFIX=limiter:
NAA_THROTTLE_USER_REGISTRATION_LIMITS=59/second
NAA_DEBUG=1
# auth0
NAA_AUTH0_DOMAIN=
NAA_AUTH0_API_AUDIENCE=
NAA_AUTH0_ISSUER=
NAA_AUTH0_CLIENT_ID=
NAA_AUTH0_CLIENT_SECRET=
NAA_AUTH0_AUTHORIZATION_URL=
# Postgres
NAA_DB_HOST=db
NAA_DB_PORT=5432
NAA_DB_NAME=
NAA_DB_USER=
NAA_DB_PASSWORD=
NAA_DB_DEFAULT_SCHEMA=public
# Redis
NAA_REDIS_HOST=redis
NAA_REDIS_PORT=6379
NAA_REDIS_THROTTLE_STORAGE_DB=2
NAA_REDIS_DEFAULT_CHARSET=utf-8
NAA_REDIS_DECODE_RESPONSES=1
NAA_REDIS_RETRY_ON_TIMEOUT=1
# Tests
TEST_CLIENT_BASE_URL=http://server:8002
```

Запуск функциональных тестов:
```shell
cd ./tests/functional && docker-compose up test
```

Или через рецепт Makefile:
```shell
make dtf
```

### Code style:
Перед коммитом проверяем, что код соответствует всем требованиям:

```shell
make lint
```

### pre-commit:
Для настройки pre-commit:
```shell
pre-commit install
```

## Трассировка
За мониторинг распределенной трассировки отвечает [Jaeger](https://www.jaegertracing.io/).
Веб-интерфейс Jaeger UI доступен по адресу:
- `http://localhost:16686/`

## Документация
Документация в формате OpenAPI 3 доступна по адресам:
- `${PROJECT_BASE_URL}/api/v1/docs` - Swagger
