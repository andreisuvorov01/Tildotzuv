# Project Features and Capabilities

## Core Functionality

### Multi-Platform Scraping
The system supports scraping from multiple Russian platforms including:
- Government procurement sites (zakupki.gov.ru, roseltorg.ru)
- Commercial platforms (avito.ru, sberbank-ast.ru)
- Specialized tender platforms (rts-tender.ru)
- Nuclear energy procurement (nep.ru)

### Advanced Anti-Detection System
The project implements multiple layers of anti-detection mechanisms:

1. **Browser Automation Stealth**:
   - WebDriver property masking
   - Plugin and language spoofing
   - WebGL and Canvas fingerprinting prevention
   - Geolocation spoofing
   - Hardware specification simulation

2. **Network Level Protection**:
   - TLS fingerprinting with curl_cffi
   - JA3/JA4 fingerprint spoofing
   - Proxy support for IP rotation
   - Account rotation system

3. **Human Behavior Simulation**:
   - Mouse movement emulation
   - Scrolling behavior simulation
   - Random delays and interactions
   - Login automation for supported platforms

### Flexible Scraping Strategies
The system automatically selects the best scraping approach based on the target platform:

1. **Request-Based Parsing**:
   - Direct HTTP requests for simple sites
   - Fast and resource-efficient
   - Used for zakupki.gov.ru, roseltorg.ru, etc.

2. **Browser-Based Scraping**:
   - Playwright integration for JavaScript-heavy sites
   - Device emulation (mobile/desktop)
   - Full browser automation capabilities

3. **Selenium WebDriver**:
   - Advanced browser automation
   - Cloudflare and anti-bot protection bypass
   - Multi-strategy approach for challenging sites

### CAPTCHA Handling
- Integration with CapSolver service
- Automatic CAPTCHA detection
- Support for ReCaptcha v2 and Cloudflare Turnstile
- Fallback mechanisms when automated solving fails

## Platform-Specific Features

### Zakupki.gov.ru
- Advanced filtering system with multiple parameters
- Support for 44-FZ, 223-FZ, and antimonopoly laws
- Price range filtering
- Date range filtering
- Sorting options (by date, price, relevance)

### RTS-tender.ru
- Multi-strategy Cloudflare bypass
- Extended timeout handling
- Challenge detection and waiting

### Sberbank-AST.ru
- JavaScript challenge handling
- Browser context management
- Session persistence

### Avito.ru
- Mobile site optimization
- Login automation support
- Account-based scraping

## User Interface Features

### Platform Selection
- Easy switching between supported platforms
- Platform-specific URL handling
- Status indicators for each platform

### Advanced Filtering
- Text search with keyword matching
- Sorting options (date, price, relevance)
- Pagination controls
- Law type filtering (44-FZ, 223-FZ, etc.)
- Price range specification
- Date range filtering

### History Tracking
- Local storage of previous searches
- Quick loading of previous filters
- History clearing functionality

### Real-Time Feedback
- Progress indicators during scraping
- Detailed error reporting
- Parser type information
- Results count display

## Technical Capabilities

### Account Management
- JSON-based account configuration
- Proxy support per account
- User agent customization
- Cookie injection for session persistence
- Profile generation with realistic data

### Docker Deployment
- Multi-container architecture (API + Frontend)
- Playwright and Chrome pre-installed
- Tor integration for additional anonymity
- Volume mounting for development
- Environment variable configuration

### Error Handling
- Comprehensive exception handling
- Fallback strategies for failed requests
- Detailed logging system
- Screenshot capture on errors
- Graceful degradation mechanisms

### Performance Optimization
- Asynchronous processing with FastAPI
- Connection pooling
- Resource cleanup
- Memory management
- Timeout handling

## Security Features

### Data Protection
- Secure credential storage
- Environment variable configuration
- Proxy-based IP rotation
- Session isolation

### Anti-Bot Measures
- Multiple fingerprinting avoidance techniques
- Human behavior simulation
- Rate limiting avoidance through account rotation
- Challenge detection and handling

### Network Security
- TLS fingerprint spoofing
- DNS resolution verification
- URL accessibility checking
- Secure header management

## Extensibility

### Parser System
- Modular parser architecture
- Easy addition of new platforms
- Base parser with common functionality
- Platform-specific customization options

### Configuration Management
- Centralized settings management
- Environment variable support
- JSON-based account configuration
- Flexible filtering system

### Integration Capabilities
- RESTful API for external integration
- Standardized data structures
- CORS support for web applications
- JSON response format

## Development Features

### Testing Support
- Multiple test files for different components
- Platform-specific test cases
- Proxy testing capabilities
- Browser automation testing

### Debugging Tools
- Screenshot capture on errors
- Detailed logging system
- Progress tracking
- Error reporting

### Development Workflow
- Docker-based development environment
- Hot reloading for frontend
- Volume mounting for code changes
- Multi-container orchestration