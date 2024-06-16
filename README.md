# Инструкция
Для запуска web сайта необходимо клонировать репозиторию и выполнить команду
```sh
docker-compose -f "docker-compose.local.yml" up --build
```
Программа автоматический создаст необходимые данные в postgresql. Также добавит тестовые данные в бд из metro_assist/base_data
 
