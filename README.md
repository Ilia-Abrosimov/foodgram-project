# foodgram-project
foodgram-project

![foodgram-project](https://github.com/Ilia-Abrosimov/foodgram-project/workflows/foodgram-project/badge.svg)

[comment]: <> (Адрес сайта)

[comment]: <> (<br>http://130.193.59.214/)
___

Приложение «Продуктовый помощник»: сайт, на котором пользователи будут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Сервис «Список покупок» позволит пользователям создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

---
Для проекта настроен Continuous Integration и Continuous Deployment: автоматический запуск тестов, обновление образов на Docker Hub и автоматический деплой на боевой сервер при пуше в ветку main

---

<h3> Технические требования и инфраструктура </h3>

- Проект использует базу данных PostgreSQL.
- Проект запускается в трёх контейнерах (Nginx, PostgreSQL и Django)

---
<h3> Установка и развертывание </h3>
После выполнения push необходимо зайти на сервер

    $ ssh <nickname>@<IP адрес>

Перейти в директорию app

    $ cd app/

Выполнить миграции

    $ docker-compose exec web python manage.py migrate

Выгрузить данные из файла csv

    $ docker-compose exec web python manage.py import_csv

Собрать статику
    
    $ docker-compose exec web python manage.py collectstatic --noinput
    
Загрузить тестовую базу

    $ docker-compose exec web python manage.py loaddata dump.json