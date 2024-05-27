## MISIS final project for Python practice. "Distributed video analytics system"

### api
- **GET** - информация о сценарии по его ID (текущий статус \ параметры работы \ ...)
- **POST** - изменение состояния стейт-машины (запуск \ остановка \ ...)

### orchestrator (orchestration \ choreography \ mix \ ...)
- **чтение события (команды)** - получение запроса от api
- **контроль состояния** - сохранение \ изменение
- **выполнение действия** - управление runner`ом

### state machine
- **PROCESSING** - процессинг видео
- **INFERENCING** - инференс видео
- **FINISHED** - успешный инференс видео

### runner & inference
- **чтение кадра** - живой поток (rtsp \ onvif \ ...) и\или заготовленное локальное видео
- **отправка кадра** - отправка кадра в сервис предсказания
- **предсказание** - inference
- **отправка результатов** - возврат результатов в runner

## How to Get Started

1. Install all required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the Docker Compose to initialize the environment:
   ```bash
   docker compose up -d
   ```
3. Start the main application:
   ```bash
   python main.py
   ```
4. Navigate to the runner directory:
   ```bash
   cd runner
   ```
5. Execute the runner script:
   ```bash
   python runner.py
   ```

Description of each row:
1. Install necessary Python packages listed in the requirements.txt file.
2. Initialize the environment using Docker Compose in detached mode.
3. Run the main application with Python.
4. Access the directory named runner.
5. Execute the Python script runner.py to perform runner tasks.