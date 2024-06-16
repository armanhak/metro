# Инструкция
Для запуска веб-сайта необходимо клонировать репозиторию и выполнить команду
```sh
docker-compose -f "docker-compose.local.yml" up --build
```
Программа автоматический создаст необходимые данные в postgresql. Также добавит тестовые данные в бд из metro_assist/base_data
## Распределение задач
Распределение задач работает отдельно от веб-сайта
Для запуска распределения задач нужно выполнить сделующие команды
```sh
pip install -m metro_assist/requirements.txt
venv/scripts/activate
python research/vrtpwt.py
```

 
