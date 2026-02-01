import React, { useState, useEffect } from 'react'

const API_BASE = 'http://localhost:8000'

function App() {
  // Доступные площадки для парсинга
  const PLATFORMS = {
    zakupki: {
      name: 'zakupki.gov.ru',
      url: 'https://zakupki.gov.ru/epz/order/extendedsearch/results.html',
      parser: 'Request-based парсер (zakupki.gov.ru)',
      status: '✅ Работает'
    },
    rosel: {
      name: 'Росэлторг',
      url: 'https://www.roseltorg.ru/procedures/search?sale=1&status%5B%5D=5&status%5B%5D=0&status%5B%5D=1&currency=all&place=fkr&source%5B%5D=13&page=1',
      parser: 'Request-based парсер (Росэлторг)',
      status: '✅ Работает'
    },
    rts: {
      name: 'РТС-тендер',
      url: 'https://www.rts-tender.ru/poisk/poisk-44-fz?keywords=',
      parser: 'Multi-strategy Cloudflare bypass',
      status: '🚀 Расширенный обход'
    },
    sber: {
      name: 'Сбербанк-АСТ',
      url: 'https://www.sberbank-ast.ru/UnitedPurchaseList.aspx',
      parser: 'Требует браузерной поддержки',
      status: '🔄 JavaScript challenge'
    },
    nep: {
      name: 'НЭП',
      url: 'https://neptek.ru/trades',
      parser: 'Request-based парсер (НЭП)',
      status: '🔄 В разработке'
    }
  }

  const [selectedPlatform, setSelectedPlatform] = useState('zakupki')
  const currentPlatform = PLATFORMS[selectedPlatform]

  const [filters, setFilters] = useState({
    search_text: '',
    sort_by: 'UPDATE_DATE',
    ascending: true,
    page: 1,
    records_per_page: 10,
    law_types: {
      fz44: true,
      fz223: true,
      af: true
    },
    price_range: {
      min: '',
      max: ''
    },
    date_range: {
      from: '',
      to: ''
    }
  })
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [history, setHistory] = useState([])
  const [parserType, setParserType] = useState('Request-based парсер (zakupki.gov.ru)')
  const [progress, setProgress] = useState(0)

  // Загружаем историю из localStorage при запуске
  useEffect(() => {
    const savedHistory = localStorage.getItem('scraperHistory')
    if (savedHistory) {
      try {
        setHistory(JSON.parse(savedHistory))
      } catch (e) {
        console.warn('Failed to load history:', e)
      }
    }
  }, [])

  // Сохраняем историю в localStorage
  const saveToHistory = (item) => {
    const newHistory = [item, ...history.slice(0, 9)] // Храним последние 10 запросов
    setHistory(newHistory)
    localStorage.setItem('scraperHistory', JSON.stringify(newHistory))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setResults(null)
    setProgress(0)

    try {
      setProgress(10)
      setParserType(currentPlatform.parser)

      const payload = {
        url: currentPlatform.url,
        filters: filters,
        platform: selectedPlatform
      }

      setProgress(30)

      const response = await fetch(`${API_BASE}/api/v1/extract-reviews`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
      })

      setProgress(60)

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const data = await response.json()
      setProgress(100)
      setResults(data)

      // Сохраняем в историю
      saveToHistory({
        url: currentPlatform.url,
        timestamp: new Date().toISOString(),
        resultsCount: data.reviews_count,
        parserType: parserType,
        filters: filters,
        platform: selectedPlatform
      })

    } catch (err) {
      setError(err.message)
      setProgress(0)
    } finally {
      setLoading(false)
    }
  }

  const updateFilter = (path, value) => {
    setFilters(prev => {
      const newFilters = { ...prev }
      const keys = path.split('.')
      let current = newFilters

      for (let i = 0; i < keys.length - 1; i++) {
        current = current[keys[i]]
      }

      current[keys[keys.length - 1]] = value
      return newFilters
    })
  }

  const loadFromHistory = (historyItem) => {
    if (historyItem.filters) {
      setFilters(historyItem.filters)
    }
    setResults(null)
    setError('')
  }

  const clearHistory = () => {
    setHistory([])
    localStorage.removeItem('scraperHistory')
  }

  return (
    <div className="container">
      <header className="header">
        <h1>🏛️ Парсер государственных закупок</h1>
        <p>Поиск и анализ закупок на ведущих электронных площадках России</p>

        <div className="platform-selector">
          <label>🏢 Выберите площадку:</label>
          <select
            value={selectedPlatform}
            onChange={(e) => setSelectedPlatform(e.target.value)}
            className="platform-select"
          >
            {Object.entries(PLATFORMS).map(([key, platform]) => (
              <option key={key} value={key}>
                {platform.name}
              </option>
            ))}
          </select>
        </div>

        <div className="parser-info">
          <span className="parser-badge">{currentPlatform.parser}</span>
          <span className={`status-badge ${currentPlatform.status.includes('✅') ? 'status-working' : 'status-developing'}`}>
            {currentPlatform.status}
          </span>
        </div>

        <div className="fixed-url">
          <strong>🎯 Источник:</strong> {currentPlatform.url}
        </div>
      </header>

      <div className="main-content">
        <div className="form-section">
          <form onSubmit={handleSubmit}>
            <div className="form-intro">
              <h3>🔧 Настройте фильтры для поиска закупок</h3>
              <p>Выберите параметры поиска и нажмите кнопку для получения результатов</p>
            </div>

            <div className="filters-grid">
              <div className="form-group">
                <label>🔍 Поисковый запрос:</label>
                <input
                  type="text"
                  value={filters.search_text}
                  onChange={(e) => updateFilter('search_text', e.target.value)}
                  placeholder="Введите ключевые слова для поиска"
                  disabled={loading}
                />
              </div>

              <div className="form-group">
                <label>📊 Сортировка:</label>
                <select
                  value={filters.sort_by}
                  onChange={(e) => updateFilter('sort_by', e.target.value)}
                  disabled={loading}
                >
                  <option value="UPDATE_DATE">По дате обновления</option>
                  <option value="PUBLISH_DATE">По дате размещения</option>
                  <option value="PRICE">По цене</option>
                  <option value="RELEVANCE">По релевантности</option>
                </select>
              </div>

              <div className="form-group">
                <label>📄 Записей на странице:</label>
                <select
                  value={filters.records_per_page}
                  onChange={(e) => updateFilter('records_per_page', parseInt(e.target.value))}
                  disabled={loading}
                >
                  <option value={10}>10 записей</option>
                  <option value={20}>20 записей</option>
                  <option value={50}>50 записей</option>
                  <option value={100}>100 записей</option>
                </select>
              </div>

              <div className="form-group price-range">
                <label>💰 Диапазон цен (руб.):</label>
                <div className="price-inputs">
                  <input
                    type="number"
                    value={filters.price_range.min}
                    onChange={(e) => updateFilter('price_range.min', e.target.value)}
                    placeholder="От"
                    disabled={loading}
                  />
                  <input
                    type="number"
                    value={filters.price_range.max}
                    onChange={(e) => updateFilter('price_range.max', e.target.value)}
                    placeholder="До"
                    disabled={loading}
                  />
                </div>
              </div>

              <div className="form-group date-range">
                <label>📅 Диапазон дат:</label>
                <div className="date-inputs">
                  <input
                    type="text"
                    value={filters.date_range.from}
                    onChange={(e) => updateFilter('date_range.from', e.target.value)}
                    placeholder="01.01.2024"
                    disabled={loading}
                  />
                  <input
                    type="text"
                    value={filters.date_range.to}
                    onChange={(e) => updateFilter('date_range.to', e.target.value)}
                    placeholder="31.12.2024"
                    disabled={loading}
                  />
                </div>
              </div>

              <div className="form-group law-types">
                <label>⚖️ Типы законов:</label>
                <div className="checkbox-group">
                  <label className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={filters.law_types.fz44}
                      onChange={(e) => updateFilter('law_types.fz44', e.target.checked)}
                      disabled={loading}
                    />
                    <span>44-ФЗ</span>
                  </label>
                  <label className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={filters.law_types.fz223}
                      onChange={(e) => updateFilter('law_types.fz223', e.target.checked)}
                      disabled={loading}
                    />
                    <span>223-ФЗ</span>
                  </label>
                  <label className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={filters.law_types.af}
                      onChange={(e) => updateFilter('law_types.af', e.target.checked)}
                      disabled={loading}
                    />
                    <span>Антимонопольное законодательство</span>
                  </label>
                </div>
              </div>
            </div>

            <button type="submit" disabled={loading}>
              {loading ? '⏳ Поиск закупок...' : '🔍 Найти закупки'}
            </button>

            {loading && (
              <div className="progress-container">
                <div className="progress-bar">
                  <div
                    className="progress-fill"
                    style={{ width: `${progress}%` }}
                  ></div>
                </div>
                <span className="progress-text">{progress}%</span>
              </div>
            )}
          </form>
        </div>

        {history.length > 0 && (
          <div className="history-section">
            <div className="history-header">
              <h3>📚 История запросов</h3>
              <button onClick={clearHistory} className="clear-history-btn">
                🗑️ Очистить
              </button>
            </div>
            <div className="history-list">
              {history.map((item, index) => (
                <div key={index} className="history-item" onClick={() => loadFromHistory(item)}>
                  <div className="history-platform">
                    🏛️ {PLATFORMS[item.platform || 'zakupki']?.name || 'zakupki.gov.ru'}
                  </div>
                  <div className="history-filters">
                    {item.filters?.search_text && <span>🔍 "{item.filters.search_text}"</span>}
                    {item.filters?.sort_by && <span>📊 {item.filters.sort_by}</span>}
                    {item.filters?.records_per_page && <span>📄 {item.filters.records_per_page} записей</span>}
                  </div>
                  <div className="history-meta">
                    <span>{new Date(item.timestamp).toLocaleString()}</span>
                    <span>{item.resultsCount} закупок</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {error && (
        <div className="error">
          ❌ Ошибка: {error}
        </div>
      )}

      {loading && (
        <div className="loading">
          🔄 Выполняется поиск закупок...
        </div>
      )}

      {results && (
        <div className="results">
          <div className="results-header">
            <h2>🏛️ Найденные закупки</h2>
            <div className="results-stats">
              <span className="stat-item">📄 Закупок: {results.reviews_count}</span>
              <span className="stat-item">⚡ {parserType}</span>
            </div>
          </div>

          <div className="results-url">
            <strong>📊 Результаты поиска по фильтрам</strong>
          </div>

          <div className="reviews-list">
            {results.reviews.map((item, index) => (
              <div key={index} className="review-item">
                <div className="review-header">
                  <div className="review-author">🏢 {item.author}</div>
                  {item.rating && (
                    <div className="review-rating">💰 {item.rating}</div>
                  )}
                </div>
                <div className="review-text">📋 {item.text}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default App