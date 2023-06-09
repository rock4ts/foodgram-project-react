![Foodgram workflow](https://github.com/rock4ts/foodgram-project-react/actions/workflows/foodgram-workflow.yml/badge.svg?event=push)

# Foodgram web-page

## **Описание проекта**

Онлайн-сервис Foodgram позволяет пользователям публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

Проект можно протестировать, перейдя по ссылке: [my-foodgram.ddns.net](my-foodgram.ddns.net)

Login / password администратора для проверки работы сайта: Ivanov / Qwerty@123
___

## **Технологии проекта**

* Python 3.9
* Django 2.2.28
* Django Rest Framework 3.12.4
* Gunicorn 20.0.4
* PostgreSQL 13.0-alpine
* Nginx 1.19.3
* Docker 19.03.0
* Docker Compose 1.25.0
___

## **Возможности веб-сервиса**

### **Главная страница**

Содержимое главной страницы — список первых шести рецептов, отсортированных по дате публикации (от новых к старым).  Остальные рецепты доступны на следующих страницах: внизу страницы есть пагинация.
___

### **Страница рецепта**

На странице — полное описание рецепта. Для авторизованных пользователей — возможность добавить рецепт в избранное и в список покупок, возможность подписаться на автора рецепта.
___

### **Страница пользователя**

На странице — имя пользователя, все рецепты, опубликованные пользователем и возможность подписаться на пользователя.
___

### **Подписка на авторов**

Подписка на публикации доступна только авторизованному пользователю. Страница подписок доступна только владельцу.

**Сценарий поведения пользователя**:

1. Пользователь переходит на страницу другого пользователя или на страницу рецепта и подписывается на публикации автора кликом по кнопке «Подписаться на автора».
2. Пользователь переходит на страницу «Мои подписки» и просматривает список рецептов, опубликованных теми авторами, на которых он подписался. Сортировка записей — по дате публикации (от новых к старым).
3. При необходимости пользователь может отказаться от подписки на автора: переходит на страницу автора или на страницу его рецепта и нажимает «Отписаться от автора».
___

### **Список избранного**

Работа со списком избранного доступна только авторизованному пользователю. Список избранного может просматривать только его владелец.

**Сценарий поведения пользователя**:

1. Пользователь отмечает один или несколько рецептов кликом по кнопке «Добавить в избранное».
2. Пользователь переходит на страницу «Список избранного» и просматривает персональный список избранных рецептов.
3. При необходимости пользователь может удалить рецепт из избранного.
___

### **Список покупок**

Работа со списком покупок доступна авторизованным пользователям. Список покупок может просматривать только его владелец.

**Сценарий поведения пользователя**:

1. Пользователь отмечает один или несколько рецептов кликом по кнопке «Добавить в покупки».
2. Пользователь переходит на страницу Список покупок, там доступны все добавленные в список рецепты. Пользователь нажимает кнопку **Скачать список** и получает файл с суммированным перечнем и количеством необходимых ингредиентов для всех рецептов, сохранённых в «Списке покупок».
3. При необходимости пользователь может удалить рецепт из списка покупок.

При скачивании списка покупок ингредиенты в результирующем списке суммируются: например, если в двух рецептах есть сахар (в одном рецепте 5 г, в другом — 10 г), то в списке будет один пункт: Сахар — 15 г.

Список покупок скачивается в формате .pdf .
___

### **Фильтрация по тегам**

При нажатии на название тега выводится список рецептов, отмеченных этим тегом. Фильтрация может проводится по нескольким тегам в комбинации «или»: если выбраны несколько тегов — в результате будут показаны рецепты, которые отмечены хотя бы одним из этих тегов.

При фильтрации на странице пользователя фильтруются только рецепты выбранного пользователя. Такой же принцип должен соблюдается при фильтрации списка избранного.
___

### **Регистрация и авторизация**

**Уровни доступа пользователей**:

* Гость (неавторизованный пользователь)
* Авторизованный пользователь
* Администратор

Что могут делать **неавторизованные пользователи**:

* Создать аккаунт.
* Просматривать рецепты на главной.
* Просматривать отдельные страницы рецептов.
* Просматривать страницы пользователей.
* Фильтровать рецепты по тегам.

Что могут делать **авторизованные пользователи**:

* Входить в систему под своим логином и паролем.
* Выходить из системы (разлогиниваться).
* Менять свой пароль.
* Создавать/редактировать/удалять собственные рецепты
* Просматривать рецепты на главной.
* Просматривать страницы пользователей.
* Просматривать отдельные страницы рецептов.
* Фильтровать рецепты по тегам.
* Работать с персональным списком избранного: добавлять в него рецепты или удалять их, просматривать свою страницу избранных рецептов.
* Работать с персональным списком покупок:
добавлять/удалять любые рецепты, выгружать файл с количеством необходимых ингредиентов для рецептов из списка покупок.
* Подписываться на публикации авторов рецептов и отменять подписку, просматривать свою страницу подписок.

Что может делать **администратор**:

Администратор обладает всеми правами авторизованного пользователя. 

Плюс к этому он может:

* Изменять пароль любого пользователя,
* Создавать/блокировать/удалять аккаунты пользователей,
* Редактировать/удалять любые рецепты,
* Добавлять/удалять/редактировать ингредиенты.
* Добавлять/удалять/редактировать теги.

Данные функции реализованы в стандартной админ-панели Django.
___

## **Запуск проекта**:

Запуск проекта производится в Docker-контейнерах, включая:

- Приложение Foodgram API;
- Приложение Foodgram Frontend;
- Сервер Nginx;
- База данных PostgreSQL.

Перед началом работы вам необходимо иметь установленный контейнизатор приложений Docker 19.03.0+, а также плагин docker compose 1.25.0+.

Файл с инструкциями для развёртывания проекта в контейнерах находится в папке `infra/`, имя файла - `docker-compose.yaml`.
___
## **Эндпоинты API**:

С  информацией об эндпоинтах и правах доступа к ресурсам API можно ознакомиться в документации, для этого перейдите по ссылке: [my-foodgram.ddns.net/api/docs/](my-foodgram.ddns.net/api/docs/)

или

[localhost/api/docs/](localhost/api/docs/) - если проект запущен локально в контейнерах.
___

### **Процедура запуска**:

**Скопируйте репозиторий на локальный компьютер:**

```
git clone git@github.com:rock4ts/foodgram-project-react.git
```
___

**Перейдите в папку `infra/`:**

```
cd infra/
```
___

**Создайте файл `.env` и указажите в нём переменные окружения согласно нижеуказанному примеру:**
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres # установите свой пароль
DB_HOST=db
DB_PORT=5432

DEBUG=False

SECRET_KEY= # сгенирируйте согласно инструкции ниже
```
___

**Для генерации SECRET_KEY:**
1. Перейдите в папку backend, создайте и активируйте виртуальное окружение выполнив команды:

```
python3 -m venv venv
```
```
source venv/bin/activate
```

2. Обновите менеджер пакетов и установите модуль Django==2.2.28:
```
python3 -m pip install --upgrade pip
```
```
pip install Django=2.2.28
```

3. Запустите интерактивный режим Django:
```
python manage.py shell
```

4. Cгенерируйте ключ, выполнив команды:
```
from django.core.management.utils import get_random_secret_key
```
```
get_random_secret_key()
```

5. Вернитесь в папку `infra/` и в файле `.env` укажите полученное значения SECRET_KEY.
___

**Запустите сборку контейнеров:**
```
docker-compose up -d --build
```

Команда запустит файл *docker-compose.yaml*, загрузит образы, cоздаст контейнеры и тома для хранения статики, медиа и данных PostgreSQL.
___

**Выполните миграции:**
```
docker-compose exec foodgram_backend python manage.py migrate
```
___

**Создайте суперпользователя для получения доступа к управлению админ-зоной:**
```
docker compose exec foodgram_backend python manage.py createsuperuser
```
___

**Заполните базу данных ингредиентами:**
```
docker compose exec foodgram_backend python manage.py from_csv_to_data
```

(Файл с табличными данными об ингридиентах находится в папке `/backend/foodgram/recipes/data/`)
___

**Зайдите в админ-зону и создайте несколько тегов:**

Они понадобятся вам при добавлении рецептов: [localhost/admin](localhost/admin)
___

**Готово!**

Главная страница проекта доступна по адресу: [localhost](localhost)

