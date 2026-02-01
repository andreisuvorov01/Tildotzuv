# Используем образ с предустановленным Playwright и Python
FROM mcr.microsoft.com/playwright/python:v1.57.0-jammy

# Устанавливаем переменные окружения для избежания интерактивных запросов
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Устанавливаем инструменты для диагностики сети и Chrome для Selenium
RUN apt-get update && apt-get install -y \
    curl \
    dnsutils \
    iputils-ping \
    wget \
    gnupg \
    tor \
    build-essential \
    libssl-dev \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    libncursesw5-dev \
    xz-utils \
    tk-dev \
    libxml2-dev \
    libxmlsec1-dev \
    libffi-dev \
    liblzma-dev \
    && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Настраиваем Tor для обхода блокировок
RUN echo "ControlPort 9051" >> /etc/tor/torrc && \
    echo "CookieAuthentication 1" >> /etc/tor/torrc

WORKDIR /app

# Установка Poetry
RUN pip install poetry

# Копируем файлы зависимостей (для кэширования слоев Docker)
COPY pyproject.toml ./

# Конфигурируем Poetry и устанавливаем зависимости
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-root --only=main

# Копируем исходный код приложения
COPY ./app ./app

# Запускаем диагностику сети при старте
RUN echo "Starting network diagnostics..."
RUN python app/test_network_docker.py || echo "Network diagnostics completed with warnings"

# Запускаем сервер
# --host 0.0.0.0 делает сервер доступным снаружи контейнера
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
