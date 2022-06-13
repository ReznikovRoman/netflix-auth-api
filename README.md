# Netflix Auth API
Сервис авторизации для онлайн-кинотеатра _Netflix_.

## Сервисы
- Netflix Admin:
  - Панель администратора для управления онлайн-кинотеатром (редактирование фильмов, жанров, актеров)
  - https://github.com/ReznikovRoman/netflix-admin
- Netflix ETL:
  - ETL пайплайн для синхронизации данных между БД сервиса Netflix Admin и Elasticsearch
  - https://github.com/ReznikovRoman/netflix-etl
- Netflix Movies API:
  - АПИ фильмов
  - https://github.com/ReznikovRoman/netflix-movies-api
- Netflix Auth API:
  - Сервис авторизации - управление пользователями и ролями
  - https://github.com/ReznikovRoman/netflix-auth-api
- Netflix UGC:
  - Сервис для работы с пользовательским контентом
  - https://github.com/ReznikovRoman/netflix-ugc

## Настройка и запуск
Docker конфигурации содержат контейнеры:
 1. server
 2. redis
 3. db
 4. traefik
 5. jaeger

Файлы docker-compose:
 1. `docker-compose.yml` - для локальной разработки
 2. `tests/functional/docker-compose.yml` - для функциональных тестов

Для запуска контейнеров нужно создать файл `.env` в корне проекта.

**Пример `.env`:**

```dotenv
ENV=.env

# Python
PYTHONUNBUFFERED=1

# Netflix Auth API
FLASK_APP=main.py
# Project
NAA_SECRET_KEY=bxv-!8yyx)boy&-spzvrc(v_%kfwuf4&47-av5zqoe(k_b=*2)
NAA_SQLALCHEMY_ECHO=1
NAA_PROJECT_BASE_URL=http://api-auth.localhost:8009
NAA_API_V1_STR=/api/v1
NAA_SERVER_HOSTS=http://api-auth.localhost:8009
NAA_SERVER_PORT=8002
NAA_PROJECT_NAME=netflix-auth
NAA_THROTTLE_KEY_PREFIX=limiter:
NAA_THROTTLE_DEFAULT_LIMITS=50/hour
NAA_THROTTLE_USER_REGISTRATION_LIMITS=5/minute
NAA_THROTTLE_ENABLE_LIMITER=1
NAA_DEBUG=1
# Tracing
NAA_OTEL_ENABLE_TRACING=1
# auth0
NAA_AUTH0_DOMAIN=dummy.com
NAA_AUTH0_API_AUDIENCE=https://dummy.com
NAA_AUTH0_ISSUER=https://dummy.com/
# Social
NAA_SOCIAL_GOOGLE_CLIENT_ID=changeme
NAA_SOCIAL_GOOGLE_CLIENT_SECRET=changeme
NAA_SOCIAL_GOOGLE_METADATA_URL=https://accounts.google.com/.well-known/openid-configuration
NAA_SOCIAL_YANDEX_CLIENT_ID=changeme
NAA_SOCIAL_YANDEX_CLIENT_SECRET=changeme
NAA_SOCIAL_YANDEX_ACCESS_TOKEN_URL=https://oauth.yandex.ru/token
NAA_SOCIAL_YANDEX_USERINFO_ENDPOINT=https://login.yandex.ru/info
NAA_SOCIAL_YANDEX_AUTHORIZE_URL=https://oauth.yandex.ru/authorize
NAA_SOCIAL_USE_STUBS=0
# Postgres
NAA_DB_HOST=db
NAA_DB_PORT=5432
NAA_DB_NAME=netflix_auth
NAA_DB_USER=yandex
NAA_DB_PASSWORD=netflix
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

**Пример `.env` (для корректной работы тестов надо подставить корректные значения для auth0):**
```dotenv
ENV=.env

# Python
PYTHONUNBUFFERED=1

# Netflix Auth API
FLASK_APP=main.py
# Project
NAA_SECRET_KEY=bxv-!8yyx)boy&-spzvrc(v_%kfwuf4&47-av5zqoe(k_b=*2)
NAA_SQLALCHEMY_ECHO=1
NAA_PROJECT_BASE_URL=http://api-auth.localhost:8009
NAA_API_V1_STR=/api/v1
NAA_SERVER_HOSTS=http://api-auth.localhost:8009
NAA_SERVER_PORT=8002
NAA_PROJECT_NAME=netflix-auth
NAA_THROTTLE_KEY_PREFIX=limiter:
NAA_THROTTLE_USER_REGISTRATION_LIMITS=59/second
NAA_THROTTLE_ENABLE_LIMITER=1
NAA_DEBUG=1
# Tracing
NAA_OTEL_ENABLE_TRACING=0
# auth0
NAA_AUTH0_DOMAIN=dummy.com
NAA_AUTH0_API_AUDIENCE=https://dummy.com
NAA_AUTH0_ISSUER=https://dummy.com/
NAA_AUTH0_CLIENT_ID=change-me
NAA_AUTH0_CLIENT_SECRET=change-me
NAA_AUTH0_AUTHORIZATION_URL=https://dummy.com/oauth/token
# Social
NAA_SOCIAL_GOOGLE_CLIENT_ID=changeme
NAA_SOCIAL_GOOGLE_CLIENT_SECRET=changeme
NAA_SOCIAL_GOOGLE_METADATA_URL=https://accounts.google.com/.well-known/openid-configuration
NAA_SOCIAL_YANDEX_CLIENT_ID=changeme
NAA_SOCIAL_YANDEX_CLIENT_SECRET=changeme
NAA_SOCIAL_YANDEX_ACCESS_TOKEN_URL=https://oauth.yandex.ru/token
NAA_SOCIAL_YANDEX_USERINFO_ENDPOINT=https://login.yandex.ru/info
NAA_SOCIAL_YANDEX_AUTHORIZE_URL=https://oauth.yandex.ru/authorize
NAA_SOCIAL_USE_STUBS=1
# Postgres
NAA_DB_HOST=db
NAA_DB_PORT=5432
NAA_DB_NAME=netflix_auth
NAA_DB_USER=yandex
NAA_DB_PASSWORD=netflix
NAA_DB_DEFAULT_SCHEMA=public
# Redis
NAA_REDIS_HOST=redis
NAA_REDIS_PORT=6379
NAA_REDIS_THROTTLE_STORAGE_DB=2
NAA_REDIS_DEFAULT_CHARSET=utf-8
NAA_REDIS_DECODE_RESPONSES=1
NAA_REDIS_RETRY_ON_TIMEOUT=1
# Tests
TEST_CLIENT_BASE_URL=http://traefik:80
TEST_SERVER_BASE_URL=http://server:8002
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
- `${PROJECT_BASE_URL}:16686/`

## Документация
Документация в формате OpenAPI 3 доступна по адресам:
- `${PROJECT_BASE_URL}/api/v1/docs` - Swagger
