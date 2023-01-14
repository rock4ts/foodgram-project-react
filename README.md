![Foodgram workflow](https://github.com/rock4ts/foodgram-project-react/actions/workflows/foodgram-workflow.yml/badge.svg?event=push)

# Foodgram web-page
## Описание
Онлайн-сервис Foodgram позволяет пользователям публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.
<br>

Проект доступен по ссылке:
[158.160.8.237](158.160.8.237)

## Основные инструменты разработки проекта
* Python 3.9
* Django 2.2.28
* Django Rest Framework 3.12.4
* React.js
* PostgreSQL 13.0-alpine
<br>

## Запуск проекта локально:

__Docker__:

Проект запускается в изолированной среде с помощью системы контейнеризации.
Перед началом работы вам необходимо иметь установленный контейнизатор приложений Docker 19.03.0+, а также плагин docker compose 1.25.0+.

Проект включает:
- Приложение Foodgram API;
- Приложение Foodgram Frontend;
- Сервер для Nginx;
- База данных PostgreSQL

Каждый сервис запускается в отдельном контейнере.
Образы автоматически загружаются с DockerHub'a. Образ для Foodgram Frontend загружается из папки frontend.

__Для запуска проекта:__

Скопируйте репозиторий на локальный компьютер:
```
git clone git@github.com:rock4ts/foodgram-project-react.git
```
Если проект запускается на удалённом сервере, в файле *nginx-foodgram/default.conf* для переменной **server_name** укажите адрес данного сервера. Адрес также необходимо добавить в переменную **ALLOWED_HOSTS** в настройках Django проекта (файл *settings.py*)

Перейдите в папку infra, __все последующие команды выполняйте из этой директории__:
```
cd <project_path>/infra/
```

Перед запуском сборки образов и создания контейнеров, в текущей директории необходимо создать файл .env и указать в нём переменные окружения согласно нижеуказанному примеру:
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres # установите свой пароль
DB_HOST=db
DB_PORT=5432

DEBUG=False
SECRET_KEY=$&05hvdh+2_@*vqnwvtdmwtme90_zpypqq2w2n(e^p=fhzah(! # не меняйте, скопируйте как есть
```
Для сборки образов и создания контейнеров выполните команду:
```
sudo docker compose -f docker-compose-foodgram.yaml up -d --build
```
Команда запустит файл *docker-compose-foodgram.yaml*, соберёт образы, cоздаст контейнеры для каждого сервиса и свяжет с томами static_value и media_value директории Nginx и API с данными медиа-файлов и статики.

Теперь в контейнере с API (при сборке ему присвоено имя foodgram_backend) необходимо выполнить миграции:

```
sudo docker compose -f docker-compose-foodgram.yaml exec foodgram_backend python manage.py migrate
```

Чтобы получить доступ к управлению базой данных через админ-зону, создайте суперпользователя:
```
sudo docker compose -f docker-compose-foodgram.yaml exec foodgram_backend python manage.py createsuperuser
```

Для удобства пользования проект содержит файл с базой данных об ингредиентах для будущих рецептов.
Заполните таблицу ингредиентов, выполнив команду:
```
sudo docker compose -f docker-compose-foodgram.yaml exec foodgram_backend python manage.py from_csv_to_data
```

Готово! Вы создали копию проекта и не можете использовать его в коммерческих целях :) 
<br>

__Детальная информация об эндпоинтах и правах доступа к API проекта доступна по ссылке__:
```
<your_server_name>/api/docs/
```
