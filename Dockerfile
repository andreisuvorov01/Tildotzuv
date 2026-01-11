# Используем образ с предустановленным Playwright и Python
FROM mcr.microsoft.com/playwright/python:v1.57.0-jammy


WORKDIR /app

# Установка Poetry
RUN pip install poetry

# Копируем файлы зависимостей (для кэширования слоев Docker)
COPY pyproject.toml ./

# Отключаем создание virtualenv, так как мы уже внутри контейнера
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi -vvv --no-root

# Копируем исходный код приложения
COPY ./app ./app

# Запускаем сервер
# --host 0.0.0.0 делает сервер доступным снаружи контейнера
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
