# Telegram-SQL-Agent
Функционал бота: 
- Получает на вход текстовый запрос на получение необходимой пользователю информации
- Проверяет полученный запрос на безопасность
- Преобразует полученный от пользователя текст в SQL-запрос 
- Выполняет сформированный SQL-запрос в определенной пользователем базе данных
- Возвращает в чат полученные данные в текстовом виде

## Содержание
- [Технологии](#технологии)
- [Разработка](#разработка)
- [To do](#to-do)
- [Команда проекта](#команда-проекта)

## Технологии
- [Python 3](https://www.python.org/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Pandas](https://pandas.pydata.org/)
- [Python-telegram-bot](https://docs.python-telegram-bot.org/)
- [PostgreSQL](https://www.postgresql.org/)
- [SQLite](https://www.sqlite.org/)
- [YandexGPT-lite](https://yandex.cloud/en/services/yandexgpt)

## Разработка

### Требования
Для установки и запуска проекта, необходим [Pip](https://pypi.org/project/pip/).

### Установка зависимостей
Для установки зависимостей, выполните команду:
```sh
$ pip install requirements.txt
```

### Добавление необходимых конфигурационных файлов
Перед запуском приложения требуется создать файл ".env" и записать в него следующие значения:
- BOT_TOKEN - [Токен вашего бота в Telegram](https://core.telegram.org/bots/tutorial/)
- YA_FOLDER_ID - [Идентификатор каталога Yandex Cloud](https://yandex.cloud/ru/docs/resource-manager/operations/folder/get-id)
- YA_API_KEY - [API-ключ Yandex Cloud](https://yandex.cloud/ru/docs/iam/concepts/authorization/api-key)

### Создание тестовой БД PostgreSQL
По умолчанию, приложение работает с двумя БД
- PostgreSQL - должна быть запущена на localhost:5431/demo
- SQLite - создается в памяти приложения

### Запуск Development сервера
Чтобы запустить сервер для разработки, выполните команду:
```sh
python agent_app.py
```

### Создание docker-контейнера
Чтобы упаковать приложение в Docker-контейнер, выполните команду: 
```sh
docker build -t innopolis-sql-agent .
```

## To do
- [ ] Настройка open-source моделей text-to-sql
- [ ] Создание отдельного фронтенда на замену Telegram

## Команда проекта
- [Веденеев Дмитрий](https://github.com/DmitryVedeneev)
