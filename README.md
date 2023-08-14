# Foodgram


### Опиание проекта.
Сайт Foodgram, «Продуктовый помощник». Это онлайн-сервис и API для него. На этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

## Проект доступен по ссылкам:

```
- https://tyrinayfoodgram.hopto.org/
- https://tyrinayfoodgram.hopto.org/admin/
```

## Учетная запись администратора:

```
- логин: admin
- почта:admin@mail.ru 
- пароль: admin
```

Foodgram - проект позволяет:

- Просматривать рецепты
- Добавлять рецепты в избранное
- Добавлять рецепты в список покупок
- Создавать, удалять и редактировать собственные рецепты
- Скачивать список покупок

## Инструкции по установке
***- Клонируйте репозиторий:***
```
git clone git@github.com:Tyrinay/foodgram-project-react.git
```

***- Подключиться к вашему серверу:***
```
ssh <server user>@<server IP>
```

***- Установите Докер на свой сервер:***
```
sudo apt install docker.io
```

***- Установите Docker Compose (для Linux):***
```
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

```

***- Получить разрешения для docker-compose:***
```
sudo chmod +x /usr/local/bin/docker-compose
```
***- Создайте каталог проекта:***
```
mkdir foodgram && cd foodgram/
```
***- Создайте env-файл:***
```
touch .env
```
***- Заполните env-файл следующим образом:***
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=<имя бд>
POSTGRES_USER=<пользователь бд>
POSTGRES_PASSWORD=<пароль бд>
DB_HOST=db
DB_PORT=5432
ALLOWED_HOSTS=*
```
***- Скопируйте файлы из 'infra/' (на вашем локальном компьютере) на ваш сервер:***
```
scp -r infra/* <server user>@<server IP>:/home/<server user>/foodgram/
```
***- Запустите docker-compose:***
```
sudo docker-compose up -d/
```

Автор: 
* [Ilya Tarnaev](https://github.com/tyrinay) :+1: