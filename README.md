# Tildotzuv
Сервис по интеграции парсера отзывов в тильду

## Интеграция Cloudflare Crawler API

В проект добавлена поддержка нового API от Cloudflare для парсинга сайтов (`/crawl` эндпоинт). Это позволяет эффективно сканировать целые сайты, получая контент в форматах HTML, Markdown или JSON.

### Настройка

Для использования API необходимо получить:
1. **Cloudflare Account ID**
2. **API Token** с разрешениями `Browser Rendering - Edit`.

Скопируйте файл `.env.example` в `.env` и заполните ваши данные:
```bash
cp .env.example .env
```

### Использование

В папке `src/` находится клиент `cloudflare_crawler.js`, который предоставляет удобный интерфейс для взаимодействия с API.

Пример использования:

```javascript
const CloudflareCrawlerClient = require('./src/cloudflare_crawler');

const client = new CloudflareCrawlerClient(process.env.CLOUDFLARE_ACCOUNT_ID, process.env.CLOUDFLARE_API_TOKEN);

async function run() {
  // Запуск задачи на сканирование
  const jobId = await client.initiateCrawl({
    url: 'https://example.com',
    limit: 10,
    formats: ['markdown']
  });

  // Ожидание завершения
  const results = await client.waitForCompletion(jobId);
  console.log('Crawl completed:', results);
}
```

Более подробный пример можно найти в `examples/crawl_example.js`.
