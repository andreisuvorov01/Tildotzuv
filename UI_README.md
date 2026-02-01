# Review Aggregator UI

Простой веб-интерфейс для сервиса парсинга отзывов с Avito и закупок с zakupki.gov.ru.

## Технологии

- **Frontend**: React 18 + Vite
- **Backend**: FastAPI (Python)
- **Контейнеризация**: Docker + Docker Compose

## Функциональность

### Основные возможности:
- Парсинг отзывов с Avito
- Парсинг закупок с zakupki.gov.ru
- Система фильтров для zakupki.gov.ru
- Отображение результатов в удобном формате

### API методы:
- `POST /api/v1/extract-reviews` - основной метод парсинга

### Фильтры для zakupki.gov.ru:
- Поисковый запрос
- Сортировка (по дате, цене, релевантности)
- Диапазон цен
- Диапазон дат
- Типы законов (ФЗ-44, ФЗ-223, Антимонопольное)
- Количество записей на странице

## Запуск

### С Docker Compose (рекомендуется):
```bash
docker-compose up --build
```

Доступ:
- Frontend: http://localhost:3000
- API: http://localhost:8000

### Локальная разработка:

Backend:
```bash
cd app
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Frontend:
```bash
cd frontend
npm install
npm run dev
```

## Использование

1. Откройте http://localhost:3000
2. Введите URL для парсинга:
   - Avito: `https://avito.ru/...`
   - Zakupki: `https://zakupki.gov.ru/...`
3. Для zakupki.gov.ru настройте фильтры
4. Нажмите "Начать парсинг"
5. Просмотрите результаты

## Структура проекта

```
├── app/                    # Backend (FastAPI)
│   ├── core/              # Основные модули
│   ├── services/          # Сервисы парсинга
│   └── main.py           # Точка входа API
├── frontend/              # Frontend (React)
│   ├── src/
│   │   ├── App.jsx       # Основной компонент
│   │   └── main.jsx      # Точка входа
│   └── package.json
└── docker-compose.yml     # Конфигурация Docker
```