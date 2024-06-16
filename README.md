# Инструкция
## Запуск веб сайта
Для запуска веб-сайта необходимо клонировать репозиторию и выполнить команду
```sh
docker-compose -f "docker-compose.local.yml" up --build
```
Программа автоматический создаст необходимые данные в postgresql. Также добавит тестовые данные в бд из <b>metro_assist/base_data</b>.<br>
Сайт будет доступен по адресу http://localhost:8000 <br><br>
Если вдруг захочется подключиться к бд через клиент, то данные для подклуючения можно брать из <b>env/.env.local</b>. Единсвтенное порт 5432 перенаправляется на 6543 (то есть нужно будет указать 6543)<br>

При желании можно запустить проект на удаленной машине. Тогда нужно будет просто создать <b>env/.env.prod</b> и указать свои данные.
На данный момент сайт работает по адресу http://62.217.177.92:8000

## Запуск распределения задач (VRPTW)
Распределение задач работает отдельно от веб-сайта. <br>
Для запуска распределения задач нужно выполнить сделующие команды (утановить менеджер пакетов pip, если еще нет. python --version 3.10)
```sh
pip install -m metro_assist/requirements.txt
venv/scripts/activate
python research/vrtpwt.py
```
После выполнения создается файл <b>"Расписание.xlsx"</b>, <br>
В файле <b>research/vrtpwt.py</b> задаются пути к файлам из <b>metro_assist/base_data</b>. Если нужно запустить на новых данных, то нужно поменять пути.

 
