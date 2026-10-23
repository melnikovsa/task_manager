# Исполняемая среда Python
FROM python:3.10-slim

# Установка системных зависимостей для сборки пакетов
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Установка рабочей директории внутри контейнера
WORKDIR /app

# Отключение буферизации вывода Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Сначала копируем только файлы конфигурации сборки для кэширования слоев Docker
COPY setup.py /app/

# Устанавливаем проект в редактируемом режиме (-e), чтобы подтянулись все install_requires
RUN pip install --no-cache-dir -e .

# Копируем весь остальной исходный код проекта
COPY . /app/

# Открываем порт 8000
EXPOSE 8000
