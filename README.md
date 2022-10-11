# Netflix Auth API
_Netflix_ authorization service.

## Stack
[Flask](https://flask.palletsprojects.com/en/2.2.x/), [Flask-RestX](https://flask-restx.readthedocs.io/en/latest/),
[SQLAlchemy](https://www.sqlalchemy.org/), [Alembic](https://alembic.sqlalchemy.org/en/latest/front.html),
[auth0](https://auth0.com/machine-to-machine),
[Postgres](https://www.postgresql.org/), [Redis](https://redis.io/)

## Services
- Netflix Admin:
  - Online-cinema management panel. Admins can manage films, genres, actors/directors/writers/...
  - https://github.com/ReznikovRoman/netflix-admin
- Netflix ETL:
  - ETL pipeline for synchronizing data between "Netflix Admin" database and Elasticsearch
  - https://github.com/ReznikovRoman/netflix-etl
- Netflix Movies API:
  - Movies API
  - https://github.com/ReznikovRoman/netflix-movies-api
    - Python client: https://github.com/ReznikovRoman/netflix-movies-client
- Netflix Auth API:
  - Authorization service - users and roles management
  - https://github.com/ReznikovRoman/netflix-auth-api
- Netflix UGC:
  - Service for working with user generated content (comments, likes, film reviews, etc.)
  - https://github.com/ReznikovRoman/netflix-ugc
- Netflix Notifications:
  - Notifications service (email, mobile, push)
  - https://github.com/ReznikovRoman/netflix-notifications
- Netflix Voice Assistant:
  - Online-cinema voice assistant
  - https://github.com/ReznikovRoman/netflix-voice-assistant

## Configuration
Docker containers:
 1. server
 2. redis
 3. db
 4. traefik
 5. jaeger

docker-compose files:
 1. `docker-compose.yml` - for local development.
 2. `tests/functional/docker-compose.yml` - for running functional tests.

To run docker containers, you need to create a `.env` file in the root directory.

**`.env` example:**
```dotenv
ENV=.env

# Python
PYTHONUNBUFFERED=1

# Netflix Auth API
FLASK_APP=auth.main
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
# Clients
NAA_CLIENT_USE_STUBS=1
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

### Start project:

Locally:
```shell
docker-compose build
docker-compose up
```

## Development
Sync environment with `requirements.txt` / `requirements.dev.txt` (will install/update missing packages, remove redundant ones):
```shell
make sync-requirements
```

Compile requirements.\*.txt files (have to re-compile after changes in requirements.\*.in):
```shell
make compile-requirements
```

Use `requirements.local.in` for local dependencies; always specify _constraints files_ (-c ...)

Example:
```shell
# requirements.local.txt

-c requirements.txt

ipython
```

### Tests
Run unit tests (export environment variables from `.env` file):
```shell
export $(echo $(cat .env | sed 's/#.*//g'| xargs) | envsubst) && make test
```

To run functional tests, you need to create `.env` in ./tests/functional directory

**`.env` example (for tests to work properly, you have to fill in correct auth0 data):**
```dotenv
ENV=.env

# Python
PYTHONUNBUFFERED=1

# Netflix Auth API
FLASK_APP=auth.main
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
# Clients
NAA_CLIENT_USE_STUBS=1
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

Run functional tests:
```shell
cd ./tests/functional && docker-compose up test
```

Makefile recipe:
```shell
make dtf
```

### Code style:
Before pushing a commit run all linters:

```shell
make lint
```

### pre-commit:
pre-commit installation:
```shell
pre-commit install
```

## Tracing
[Jaeger](https://www.jaegertracing.io/) is responsible for distributed tracing.
Jaeger UI web interface:
- `${PROJECT_BASE_URL}:16686/`

## Documentation
OpenAPI 3 documentation:
- `${PROJECT_BASE_URL}/api/v1/docs` - Swagger
