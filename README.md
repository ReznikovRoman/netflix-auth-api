# Netflix API
Сервис авторизации для онлайн-кинотеатра _Netflix_.

## Сервисы
- Netflix Admin: https://github.com/ReznikovRoman/netflix-admin
- Netflix ETL: https://github.com/ReznikovRoman/netflix-etl
- Netflix Movies API: https://github.com/ReznikovRoman/netflix-movies-api
- Netflix Auth API: https://github.com/ReznikovRoman/netflix-auth-api

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
