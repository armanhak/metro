# Инструкция

## Запуск веб сайта


Для запуска веб-сайта необходимо клонировать репозиторию и выполнить команду
```sh
docker-compose -f "docker-compose.local.yml" up --build
```
Программа автоматически создаст необходимые данные в PostgreSQL. Также добавит тестовые данные в базу данных из <b>metro_assist/base_data</b>.<br>
Сайт будет доступен по адресу http://localhost:8000 <br><br>
Если захочется подключиться к базе данных через клиент, то данные для подключения можно взять из <b>env/.env.local</b>. Единственное, порт 5432 перенаправляется на 6543 (то есть нужно будет указать 6543).<br>

При желании можно запустить проект на удаленной машине. Тогда нужно будет просто создать <b>env/.env.prod</b> и указать свои данные.
На данный момент сайт работает по адресу http://62.217.177.92:8000.

### Рабочий функционал

 - Главная страница (список заявок)
 - Создание нового пасажира
 - Создание новой заявки
   - Поиск и выбор пассажира
   - Поиск и выбор станции метро
   - Автоматческое определение time_over (время поездки от начальной станции до конечной)
   - Построение маршрута поездки с указанием пересадок, если их есть
   - Автоматическое определение категории заявки согласно выбранному пасажира (есть возможность поменять)
 - Создание сотрудника (частично)
 - Личный кабинет
   - Проектирована вся база, есть возможность регистрировать пользователей, но на front-end не добавили фцнкционал
 - Административный панель
    - Подключили административную панель Django, что дает возможность управлять всю база

## Запуск распределения задач (VRPTW)
Распределение задач работает отдельно от веб-сайта. <br>
Для запуска распределения задач нужно выполнить следующие команды (установить менеджер пакетов pip, если еще нет, и использовать python версии 3.10):
```sh
pip install -m metro_assist/requirements.txt
venv/scripts/activate
python research/vrtpwt.py
```
После выполнения создается файл <b>"Расписание.xlsx"</b>.<br>
В файле <b>research/vrtpwt.py</b> задаются пути к файлам из <b>metro_assist/base_data</b>. Если нужно запустить на новых данных, то нужно поменять пути.
### Информация по скорости и по кол-ву выполненных задач
 - Железо: <b>intel core i7-11800H</b>
 - Скорость составления матриц расстояний между задачами: <b>76.22 сек</b> (составление/обновление матрицы планируем сделать с каждой добавленной задачей. Это позволит за миллисекунды получить матрицы расстояний)
 - Скорость назначения задач: <b>27.66 сек</b>
 - Количество назначенных задач: <b>506</b> из <b>713</b> (по каждой задаче могут быть более одного назначения)
 
