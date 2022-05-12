# Netflix Auth API
Сервис аутентификации для онлайн-кинотеатра.

## Технологии
- Flask
  - [flask-sqlalchemy](https://flask-sqlalchemy.palletsprojects.com/en/2.x/quickstart/)
    - Дополнение к ORM SQLAlchemy
  - [flask-restx](https://flask-restx.readthedocs.io/en/latest/)
    - REST API + Swagger docs
  - [flask-pydantic](https://github.com/bauerji/flask-pydantic)
    - Валидация данных
  - [flask-jwt-extended](https://flask-jwt-extended.readthedocs.io/en/stable/basic_usage/)
    - Генерация JWT токенов
  - [authlib](https://docs.authlib.org/en/latest/client/flask.html#flask-client)
    - OAuth 2.0
  - [flask-limiter](https://github.com/alisaifee/flask-limiter)
    - Rate limits
- PostgreSQL
  - Основная БД для хранения информации о пользователях, ролях и социальных аккаунтах
- Redis
  - Хранилище недействительных access токенов (токенов, у которых истек `ttl`),
  а также refresh токенов с установленным `ttl`

## АПИ
- Анонимный пользователь
  - Авторизация через социальную сеть
    - `POST /api/v1/social/login/{provider_name}`
    - ? Тело запроса
    - Google OAuth
    - Yandex OAuth
  - Вход в аккаунт через социальную сеть
    - `POST /api/v1/social/login/{provider_slug}`
    - ? Тело запроса
    - Google OAuth
    - Yandex OAuth
  - Стандартная регистрация по электронной почте и паролю
    - `POST /api/v1/auth/register`
    - Тело запроса
    ```json
    {
      "login": "xxx@mail.com",
      "password": "xxx"
    }
    ```
  - Стандартный вход в аккаунт по электронной почте и паролю
    - `POST /api/v1/auth/login`
    - Тело запроса
    ```json
    {
      "login": "xxx@mail.com",
      "password": "xxx"
    }
    ```
  - Обновление access токена с помощью refresh токена
    - `POST /api/v1/auth/refresh`
    - Тело запроса
    ```json
    {
      "refresh_token": "xxx",
      "grant_type": "refresh_token"
    }
    ```
  - Выход из аккаунта
    - `POST /api/v1/auth/logout`
- Авторизированный пользователь
  - Изменение пароля
    - `POST /api/v1/users/me/change-password`
    - Тело запроса
    ```json
    {
      "old_password": "old",
      "new_password": "new",
      "new_password_confirmation": "new"
    }
    ```
  - Просмотр истории входов в аккаунт
    - `GET /api/v1/users/me/login-history`
    - ID лога (истории входа)
    - ID пользователя
    - User Agent, с которого был произведен вход в аккаунт
    - Дата входа в аккаунт
    - Доп. информация о входе
  - Просмотр списка связанных аккаунтов в социальных сетях
    - `GET /api/v1/users/me/social-accounts/`
  - Открепление аккаунта из социальной сети
    - `DELETE /api/v1/users/me/social-accounts/{social_account_id}`
- Роли
  - Приватное АПИ
    - CLIENT_ID/CLIENT_SECRET
    - Используем сервис auth0 для генерации и проверки ключей
  - CRUD
    - Создание новой роли
      - `POST /api/v1/roles/`
      - Тело запроса
      ```json
        {
          "name": "xxx",
          "description": "xxx"
        }
      ```
    - Удаление роли
      - `DELETE /api/v1/roles/{role_id}`
    - Изменение роли
      - `PATCH /api/v1/roles/{role_id}`
      - Тело запроса
      ```json
        {
          "name": "xxx",
          "description": "xxx"
        }
      ```
    - Просмотр всех ролей
      - `GET /api/v1/roles/`
  - Назначение роли пользователю
    - `POST /api/v1/users/{user_id}/roles/{role_id}`
  - Удалить роль у пользователя
    - `DELETE /api/v1/users/{user_id}/roles/{role_id}`
  - Проверка наличия роли у пользователя. 200 - роль есть, 404 - роли у пользователя нет
    - `HEAD /api/v1/users/{user_id}/roles/{role_id}/`
