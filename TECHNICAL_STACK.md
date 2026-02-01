# Technical Stack and Dependencies

## Backend Technologies

### Core Framework
- **Python 3.10+**: Primary programming language
- **FastAPI**: High-performance web framework for building APIs with automatic interactive documentation
- **Pydantic**: Data validation and settings management using Python type annotations

### Web Scraping Tools
- **Playwright**: Browser automation library for reliable end-to-end testing
- **BeautifulSoup4**: HTML and XML parser for extracting data from web pages
- **curl-cffi**: Python binding for libcurl with JA3/JA4 fingerprint spoofing capabilities
- **Selenium**: Browser automation tool for advanced scraping scenarios
- **webdriver-manager**: Driver management for Selenium WebDriver
- **requests-html**: Pythonic HTML parsing with JavaScript support
- **cloudscraper**: Library for bypassing Cloudflare's anti-bot protection
- **undetected-chromedriver**: Modified Selenium driver for evading bot detection

### Anti-Detection and Stealth
- **playwright-stealth**: Stealth mode for Playwright to avoid bot detection
- **fake-useragent**: User agent generator for browser fingerprinting

### CAPTCHA Solving
- **capsolver**: Python SDK for CapSolver CAPTCHA solving service

### Data Management
- **Pydantic**: Data validation and serialization
- **Pydantic-settings**: Settings management for applications

### Asynchronous Processing
- **asyncio**: Python's built-in library for writing concurrent code using async/await syntax

### Logging and Utilities
- **logging**: Python's built-in logging module
- **urllib**: URL handling and parsing
- **json**: JSON encoding and decoding

## Frontend Technologies

### Core Framework
- **React 18+**: JavaScript library for building user interfaces
- **Vite**: Next-generation frontend tooling with fast development server

### Development Dependencies
- **@types/react**: TypeScript definitions for React
- **@types/react-dom**: TypeScript definitions for React DOM
- **@vitejs/plugin-react**: React plugin for Vite
- **vite**: Frontend build tool

## Infrastructure and Deployment

### Containerization
- **Docker**: Container platform for consistent deployment
- **Docker Compose**: Multi-container Docker application orchestration

### Browser Automation
- **Google Chrome/Chromium**: Browser for Selenium automation
- **Playwright Browsers**: Pre-installed browsers for Playwright automation

### Networking
- **Tor**: Optional anonymity network integration

### Package Management
- **Poetry**: Python dependency management and packaging tool
- **npm**: Node.js package manager for frontend dependencies

## Key Dependencies Breakdown

### Python Dependencies (pyproject.toml)

#### Web Framework
- **fastapi ^0.109.0**: Modern, fast web framework
- **uvicorn ^0.27.0**: ASGI server implementation

#### Browser Automation
- **patchright ^1.57.0**: Playwright fork with additional features
- **playwright-stealth ^1.0.6**: Stealth mode for Playwright
- **selenium ^4.17.2**: Browser automation framework
- **webdriver-manager ^4.0.1**: Driver management for Selenium
- **undetected-chromedriver ^3.5.5**: Modified ChromeDriver to evade bot detection

#### Web Scraping
- **beautifulsoup4 ^4.12.0**: HTML/XML parser
- **requests-html ^0.10.0**: HTML parsing with JavaScript support
- **cloudscraper ^1.2.71**: Cloudflare bypass library
- **curl-cffi ^0.5.10**: libcurl binding with JA3 fingerprint spoofing

#### Data Validation
- **pydantic ^2.6.0**: Data validation using Python type hints
- **pydantic-settings ^2.12.0**: Settings management

#### CAPTCHA Solving
- **capsolver ^1.0.0**: CapSolver API client

#### Anti-Detection
- **fake-useragent ^1.4.0**: User agent generator

### Node.js Dependencies (package.json)

#### Core Libraries
- **react ^18.2.0**: UI library
- **react-dom ^18.2.0**: DOM-specific methods for React

#### Development Tools
- **@vitejs/plugin-react ^4.2.1**: React plugin for Vite
- **vite ^5.0.8**: Frontend build tool

## System Architecture

### Backend Services
```
FastAPI Application
├── Core Services
│   ├── Browser Manager (Playwright)
│   ├── Account Manager (JSON)
│   ├── Network Handler (curl-cffi)
│   ├── Stealth Engine
│   ├── Humanization Engine
│   └── CAPTCHA Solver (CapSolver)
├── Scraping Engine
│   ├── Parser System
│   │   ├── Base Parser
│   │   ├── Zakupki Parser
│   │   ├── Roseltorg Parser
│   │   ├── RTS Tender Parser
│   │   ├── Sberbank AST Parser
│   │   ├── Avito Parser
│   │   ├── Books.toscrape Parser
│   │   ├── Quotes Parser
│   │   └── NEP Parser
│   └── Multi-Strategy Executor
│       ├── Request-Based Scraper
│       ├── Browser-Based Scraper
│       └── Selenium Scraper
└── API Endpoints
    ├── Review Extraction
    ├── Selenium Testing
    ├── Cloudflare Bypass Testing
    └── RTS Tender Testing
```

### Frontend Components
```
React Application
├── Platform Selector
├── Filter Configuration
│   ├── Text Search
│   ├── Sorting Options
│   ├── Pagination
│   ├── Law Type Filters
│   ├── Price Range
│   └── Date Range
├── History Management
├── Results Display
└── Progress Tracking
```

### Docker Architecture
```
Docker Environment
├── API Service
│   ├── Python 3.10+
│   ├── Playwright
│   ├── Chrome/Chromium
│   ├── Tor (optional)
│   └── Dependencies
└── Frontend Service
    ├── Node.js 18+
    ├── React
    └── Vite
```

## Development Workflow

### Backend Development
1. Python development with FastAPI
2. Playwright for browser automation
3. Docker for consistent environments
4. Poetry for dependency management

### Frontend Development
1. React development with Vite
2. npm for package management
3. Docker for consistent environments

### Testing
1. Unit testing with pytest
2. Integration testing with Docker
3. Browser testing with Playwright

## Deployment Architecture

### Production Environment
- **Container Orchestration**: Docker Compose
- **Load Balancing**: Built-in with Docker
- **Scaling**: Horizontal scaling through Docker replication
- **Monitoring**: Docker logs and health checks

### Development Environment
- **Hot Reloading**: Vite for frontend, Uvicorn for backend
- **Volume Mounting**: Direct code changes reflected in containers
- **Environment Variables**: Configuration through .env files

## Security Considerations

### Data Protection
- Secure credential storage in environment variables
- JSON-based account configuration with encryption capability
- Proxy-based IP rotation for anonymity

### Network Security
- TLS fingerprint spoofing with curl-cffi
- DNS resolution verification
- URL accessibility checking
- Secure header management

### Anti-Detection
- Multiple fingerprinting avoidance techniques
- Human behavior simulation
- Rate limiting avoidance through account rotation
- Challenge detection and handling

## Performance Optimization

### Resource Management
- Asynchronous processing with FastAPI
- Connection pooling
- Resource cleanup
- Memory management
- Timeout handling

### Caching
- Browser context reuse
- Session persistence
- Cookie injection
- Local storage for history

### Scalability
- Multi-container architecture
- Horizontal scaling capabilities
- Load distribution
- Resource isolation