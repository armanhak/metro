# Инструкция
## Запуск веб сайта
Для запуска веб-сайта необходимо клонировать репозиторию и выполнить команду
```sh
docker-compose -f "docker-compose.local.yml" up --build
```
Программа автоматический создаст необходимые данные в postgresql. Также добавит тестовые данные в бд из metro_assist/base_data.<br>
Сайт будет доступен по адресу http://localhost:8000
## Распределение задач
Распределение задач работает отдельно от веб-сайта. <br>
Для запуска распределения задач нужно выполнить сделующие команды
```sh
pip install -m metro_assist/requirements.txt
venv/scripts/activate
python research/vrtpwt.py
```
После выполнения создается файл "Расписание.xlsx", <br>
В файле <b>research/vrtpwt.py</b> берутся составляется 

 
