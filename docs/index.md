# Netflix Auth API
Authentication service for the online cinema.

## Technologies
- Flask
  - [flask-sqlalchemy](https://flask-sqlalchemy.palletsprojects.com/en/2.x/quickstart/)
    - SQLAlchemy ORM Flask extension
  - [flask-migrate](https://flask-migrate.readthedocs.io/en/latest/)
    - Alembic migrations extension
  - [flask-security](https://pythonhosted.org/Flask-Security/quickstart.html)
    - User management
  - [flask-restx](https://flask-restx.readthedocs.io/en/latest/)
    - REST API + Swagger docs
  - [flask-jwt-extended](https://flask-jwt-extended.readthedocs.io/en/stable/basic_usage/)
    - JWT manager
  - [authlib](https://docs.authlib.org/en/latest/client/flask.html#flask-client)
    - Social Auth, OAuth 2.0
  - [flask-limiter](https://github.com/alisaifee/flask-limiter)
    - Rate limits
- PostgreSQL
  - Primary database for storing information about users, roles and social accounts.
- Redis
  - Storage of invalid access tokens (tokens with expired `ttl`) and refresh tokens with configured `ttl`

## API
- Anonymous user
  - Social login
    - `POST /api/v1/social/login/{provider_slug}`
    - ? Request body
    - Google OAuth
    - Yandex OAuth
  - Standard email-password registration
    - `POST /api/v1/auth/register`
    - Request body
    ```json
    {
      "login": "xxx@mail.com",
      "password": "xxx"
    }
    ```
  - Email-password login/authentication
    - `POST /api/v1/auth/login`
    - Request body
    ```json
    {
      "login": "xxx@mail.com",
      "password": "xxx"
    }
    ```
  - Retrieve a new access token by the refresh token
    - `POST /api/v1/auth/refresh`
    - Request body
    ```json
    {
      "refresh_token": "xxx",
      "grant_type": "refresh_token"
    }
    ```
  - Logout
    - `POST /api/v1/auth/logout`
- Authenticated user
  - Change password
    - `POST /api/v1/users/me/change-password`
    - Request body
    ```json
    {
      "old_password": "old",
      "new_password1": "new",
      "new_password2": "new"
    }
    ```
  - View account login history
    - `GET /api/v1/users/me/login-history`
    - Log ID (login history)
    - User ID
    - User Agent, from which the account was logged in
    - Login date
    - Additional login information
  - List of linked social accounts
    - `GET /api/v1/users/me/social-accounts/`
  - Remove integration with a social account
    - `DELETE /api/v1/users/me/social-accounts/{social_account_id}`
- Roles
  - Private API
    - CLIENT_ID/CLIENT_SECRET
    - We use the auth0 service to generate and verify keys
  - CRUD
    - Create role
      - `POST /api/v1/roles/`
      - Request body
      ```json
        {
          "name": "xxx",
          "description": "xxx"
        }
      ```
    - Delete role
      - `DELETE /api/v1/roles/{role_id}`
    - Change role
      - `PATCH /api/v1/roles/{role_id}`
      - Request body
      ```json
        {
          "name": "xxx",
          "description": "xxx"
        }
      ```
    - List of all roles
      - `GET /api/v1/roles/`
  - Assign role to the user
    - `POST /api/v1/users/{user_id}/roles/{role_id}`
  - Remove role from the user
    - `DELETE /api/v1/users/{user_id}/roles/{role_id}`
  - Проверка наличия роли у пользователя. 200 - роль есть, 404 - роли у пользователя нет
  - Check whether user has a specific role. 200 - user has the given role, 404 otherwise
    - `HEAD /api/v1/users/{user_id}/roles/{role_id}/`
