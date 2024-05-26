# video_analytics_project
MISIS final project for Infrastructure Python

## Распределенная система видео аналитики

### uml
- https://habr.com/ru/companies/alfa/articles/740518/

## api
- **GET** - информация о сценарии по его ID (текущий статус \ параметры работы \ ...)
- **POST** - изменение состояния стейт-машины (запуск \ остановка \ ...)

### docs
- https://fastapi.tiangolo.com/
- https://github.com/aio-libs/aiokafka
### healthcheck
- https://habr.com/ru/companies/nixys/articles/544288/
- https://github.com/peter-evans/docker-compose-healthcheck

## orchestrator (orchestration \ choreography \ mix \ ...)
- **чтение события (команды)** - получение запроса от api
- **контроль состояния** - сохранение \ изменение
- **выполнение действия** - управление runner`ом

### state machine
- **init_startup** - инициализация запуска
- **in_startup_processing** - промежуточное состояние, олицетворяющее процесс запуска
- **init_shutdown** - инициализация остановки
- **in_shutdown_processing** - промежуточное состояние, олицетворяющее процесс остановки
- **active** - активная состояние \ работа 
- **inactive** - выключенное состояние

## runner
- **чтение кадра** - живой поток (rtsp \ onvif \ ...) и\или заготовленное локальное видео
- **отправка кадра** - отправка кадра в сервис предсказания
- **получение результата** - чтение результатов с предсказаниями

## inference
- **чтение кадра** - получение кадра из очереди
- **предсказание** - inference
- **отправка результатов** - возврат результатов в runner
