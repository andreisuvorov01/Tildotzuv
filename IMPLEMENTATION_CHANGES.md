# Detailed Implementation Changes

## 1. Enable Stealth Functionality

### File: app/core/browser.py
**Change**: Enable stealth functionality in the new_page method

**Current Code** (lines 103-107):
```python
async def new_page(self, context: BrowserContext):
    page = await context.new_page()
    # Временно отключаем stealth для тестирования
    logger.info("Running without stealth for testing")
    return page
```

**Required Change**:
```python
async def new_page(self, context: BrowserContext):
    page = await context.new_page()
    # Enable stealth for production
    if stealth_async:
        await stealth_async(page)
        logger.info("Stealth mode enabled")
    return page
```

## 2. Enhance Stealth Implementation

### File: app/core/stealth.py
**Change**: Add additional stealth techniques

**Add these techniques to the existing stealth implementation**:

```javascript
// 12. Mask WebGL debug renderer info
const getParameter = WebGLRenderingContext.prototype.getParameter;
WebGLRenderingContext.prototype.getParameter = function(parameter) {
    // UNMASKED_VENDOR_WEBGL
    if (parameter === 37445) {
        return 'Google Inc. (NVIDIA)';
    }
    // UNMASKED_RENDERER_WEBGL
    if (parameter === 37446) {
        return 'ANGLE (NVIDIA, NVIDIA GeForce GTX 1050 Ti Direct3D11 vs_5_0 ps_5_0, D3D11-27.21.14.5655)';
    }
    return getParameter(parameter);
};

// 13. Mask battery API
if (navigator.getBattery) {
    const getBattery = navigator.getBattery;
    navigator.getBattery = function() {
        return Promise.resolve({
            charging: true,
            chargingTime: 0,
            dischargingTime: Infinity,
            level: 0.95
        });
    };
}

// 14. Mask screen properties
Object.defineProperty(Screen.prototype, 'availWidth', {
    get: () => window.screen.width
});
Object.defineProperty(Screen.prototype, 'availHeight', {
    get: () => window.screen.height
});

// 15. Mask touch support
Object.defineProperty(navigator, 'maxTouchPoints', {
    get: () => 0
});
Object.defineProperty(navigator, 'msMaxTouchPoints', {
    get: () => 0
});

// 16. Mask connection information
if (navigator.connection) {
    Object.defineProperty(navigator.connection, 'effectiveType', {
        get: () => '4g'
    });
    Object.defineProperty(navigator.connection, 'downlink', {
        get: () => 10
    });
    Object.defineProperty(navigator.connection, 'rtt', {
        get: () => 50
    });
}
```

## 3. Enhanced User Agent Rotation

### File: app/core/accounts.py
**Change**: Add dynamic user agent generation

**Add to the AccountManager class**:
```python
def generate_user_agent(self) -> str:
    """Generate a realistic user agent"""
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15"
    ]
    return random.choice(user_agents)

def get_account_with_rotating_ua(self) -> Optional[Dict[str, Any]]:
    """Get account with rotating user agent"""
    account = self.get_random_account()
    if account:
        # Generate new user agent for each request
        account['user_agent'] = self.generate_user_agent()
    return account
```

## 4. Advanced Human Behavior Simulation

### File: app/core/humanization.py
**Change**: Enhance human behavior simulation

**Replace the existing functions with enhanced versions**:

```python
async def human_behavior_simulation(page):
    """Advanced human behavior simulation"""
    try:
        # Get viewport size
        viewport = await page.viewport_size()
        
        # Random mouse movements
        for _ in range(random.randint(3, 7)):
            x = random.randint(0, viewport['width'] - 1)
            y = random.randint(0, viewport['height'] - 1)
            await page.mouse.move(x, y)
            await asyncio.sleep(random.uniform(0.1, 0.5))
        
        # Random scrolling with pauses
        scroll_height = await page.evaluate("document.body.scrollHeight")
        current_pos = 0
        max_scroll = min(scroll_height, 5000)  # Limit scrolling to reasonable amount
        
        while current_pos < max_scroll:
            scroll_step = random.randint(100, 300)
            current_pos += scroll_step
            await page.evaluate(f"window.scrollTo(0, {min(current_pos, max_scroll)})")
            
            # Random pause
            if random.random() < 0.3:
                await asyncio.sleep(random.uniform(0.5, 2.0))
            
            # Small delay between scrolls
            await asyncio.sleep(random.uniform(0.05, 0.2))
        
        # Random element interaction (if elements exist)
        try:
            elements = await page.query_selector_all("a, button, input")
            if elements and random.random() < 0.5:  # 50% chance to interact
                element = random.choice(elements[:min(5, len(elements))])  # First 5 elements
                await element.hover()
                await asyncio.sleep(random.uniform(0.1, 0.3))
                
                # Occasionally click (but not on links that would navigate)
                if random.random() < 0.2 and "input" in str(element):
                    await element.click()
                    await asyncio.sleep(random.uniform(0.5, 1.0))
        except Exception as e:
            logger.debug(f"Element interaction failed: {e}")
            
    except Exception as e:
        logger.warning(f"Human behavior simulation failed: {e}")

async def realistic_typing(page, selector: str, text: str):
    """Simulate realistic typing with random delays"""
    try:
        element = await page.query_selector(selector)
        if element:
            for char in text:
                await element.type(char)
                # Random delay between keystrokes (50-200ms)
                await asyncio.sleep(random.uniform(0.05, 0.2))
    except Exception as e:
        logger.warning(f"Realistic typing failed: {e}")
        # Fallback to regular typing
        await page.fill(selector, text)
```

## 5. Enhanced CAPTCHA Detection

### File: app/core/captcha.py
**Change**: Improve CAPTCHA detection capabilities

**Replace the detect_and_solve_captcha method**:

```python
async def detect_and_solve_captcha(self, page, url: str) -> bool:
    """
    Enhanced CAPTCHA detection with multiple techniques
    """
    if not self.solver:
        return False
    
    # Enhanced CAPTCHA indicators
    captcha_indicators = [
        # ReCaptcha
        ".g-recaptcha", "[data-sitekey]", ".recaptcha-checkbox",
        # hCaptcha
        "[data-hcaptcha-sitekey]", ".h-captcha",
        # Cloudflare
        ".cf-turnstile", "#challenge-form", ".captcha",
        # Generic
        "iframe[src*='captcha']", "[id*='captcha']", "[class*='captcha']",
        # Text-based detection
        "captcha", "recaptcha", "hcaptcha", "turnstile"
    ]
    
    # Check for visible CAPTCHA elements
    for selector in captcha_indicators:
        try:
            elements = await page.query_selector_all(selector)
            if elements:
                logger.info(f"CAPTCHA detected with selector: {selector}")
                
                # Try to solve based on type
                if "g-recaptcha" in selector or "[data-sitekey]" in selector:
                    return await self._solve_recaptcha_v2(page, url)
                elif "hcaptcha" in selector:
                    return await self._solve_hcaptcha(page, url)
                elif "cf-turnstile" in selector:
                    return await self._solve_cloudflare_turnstile(page, url)
                else:
                    # Try generic solving
                    return await self._solve_generic_captcha(page, url)
        except Exception as e:
            logger.debug(f"CAPTCHA detection error for {selector}: {e}")
            continue
    
    # Check for CAPTCHA text in page content
    try:
        content = await page.content()
        content_lower = content.lower()
        captcha_keywords = ["captcha", "robot", "verification", "challenge", "not a robot"]
        
        if any(keyword in content_lower for keyword in captcha_keywords):
            logger.info("Potential CAPTCHA detected by content analysis")
            # Try to solve with available methods
            return await self._solve_generic_captcha(page, url)
    except Exception as e:
        logger.debug(f"Content-based CAPTCHA detection failed: {e}")
    
    return False

async def _solve_recaptcha_v2(self, page, url: str) -> bool:
    """Solve ReCaptcha v2"""
    try:
        # Find site key
        recaptcha_element = await page.query_selector("[data-sitekey]")
        if not recaptcha_element:
            return False
            
        site_key = await recaptcha_element.get_attribute("data-sitekey")
        if not site_key:
            return False
            
        # Solve with CapSolver
        solution = self.solver.recaptcha_v2(site_key=site_key, url=url)
        token = solution.get("gRecaptchaResponse", "")
        
        if token:
            # Inject token
            await page.evaluate(f"""
                document.querySelector('[name="g-recaptcha-response"]').value = '{token}';
            """)
            logger.info("ReCaptcha v2 solved successfully")
            return True
    except Exception as e:
        logger.error(f"ReCaptcha v2 solving failed: {e}")
    
    return False

async def _solve_hcaptcha(self, page, url: str) -> bool:
    """Solve hCaptcha"""
    try:
        # Find site key
        hcaptcha_element = await page.query_selector("[data-hcaptcha-sitekey]")
        if not hcaptcha_element:
            return False
            
        site_key = await hcaptcha_element.get_attribute("data-hcaptcha-sitekey")
        if not site_key:
            return False
            
        # Solve with CapSolver
        solution = self.solver.hcaptcha(site_key=site_key, url=url)
        token = solution.get("captchaResponse", "")
        
        if token:
            # Inject token
            await page.evaluate(f"""
                document.querySelector('[name="h-captcha-response"]').value = '{token}';
            """)
            logger.info("hCaptcha solved successfully")
            return True
    except Exception as e:
        logger.error(f"hCaptcha solving failed: {e}")
    
    return False

async def _solve_cloudflare_turnstile(self, page, url: str) -> bool:
    """Solve Cloudflare Turnstile"""
    try:
        # Solve with CapSolver
        solution = self.solver.cloudflare_turnstile(url=url)
        token = solution.get("token", "")
        
        if token:
            # Inject token
            await page.evaluate(f"""
                document.querySelector('[name="cf-turnstile-response"]').value = '{token}';
            """)
            logger.info("Cloudflare Turnstile solved successfully")
            return True
    except Exception as e:
        logger.error(f"Cloudflare Turnstile solving failed: {e}")
    
    return False

async def _solve_generic_captcha(self, page, url: str) -> bool:
    """Generic CAPTCHA solving attempt"""
    # Try different solving methods
    methods = [
        self._solve_recaptcha_v2,
        self._solve_hcaptcha,
        self._solve_cloudflare_turnstile
    ]
    
    for method in methods:
        try:
            if await method(page, url):
                return True
        except:
            continue
    
    return False
```

## 6. Enhanced Proxy Management

### File: app/core/accounts.py
**Change**: Add proxy management capabilities

**Add to the AccountManager class**:

```python
class ProxyManager:
    def __init__(self):
        self.proxies = [
            # Add quality proxies here
            # Format: {"server": "http://proxy:port", "username": "user", "password": "pass"}
        ]
        self.failed_proxies = set()
        self.proxy_stats = {}
    
    def add_proxy(self, proxy_config: dict):
        """Add a proxy to the pool"""
        self.proxies.append(proxy_config)
        self.proxy_stats[str(proxy_config)] = {
            "success_count": 0,
            "fail_count": 0,
            "last_used": None
        }
    
    def get_working_proxy(self) -> Optional[dict]:
        """Get a working proxy that hasn't failed recently"""
        working_proxies = [p for p in self.proxies if str(p) not in self.failed_proxies]
        if working_proxies:
            return random.choice(working_proxies)
        return None
    
    def mark_proxy_success(self, proxy_config: dict):
        """Mark a proxy as successful"""
        proxy_key = str(proxy_config)
        if proxy_key in self.proxy_stats:
            self.proxy_stats[proxy_key]["success_count"] += 1
            self.proxy_stats[proxy_key]["last_used"] = datetime.now()
        # Remove from failed list if it was there
        self.failed_proxies.discard(proxy_key)
    
    def mark_proxy_failed(self, proxy_config: dict):
        """Mark a proxy as failed"""
        proxy_key = str(proxy_config)
        self.failed_proxies.add(proxy_key)
        if proxy_key in self.proxy_stats:
            self.proxy_stats[proxy_key]["fail_count"] += 1
            self.proxy_stats[proxy_key]["last_used"] = datetime.now()
    
    def get_proxy_stats(self) -> dict:
        """Get proxy statistics"""
        return self.proxy_stats

# Global proxy manager instance
proxy_manager = ProxyManager()
```

## 7. Enhanced TLS Fingerprinting

### File: app/core/network.py
**Change**: Add TLS fingerprint rotation

**Add TLS profile management**:

```python
# Add at the top of the file
TLS_PROFILES = {
    "chrome_110": "chrome110",
    "chrome_100": "chrome100", 
    "firefox_110": "firefox_110",
    "safari_16": "safari_16_0"
}

def get_random_tls_profile() -> str:
    """Get a random TLS profile"""
    return random.choice(list(TLS_PROFILES.values()))

# Modify check_url_accessibility function
async def check_url_accessibility(url: str, tls_profile: str = None) -> bool:
    """
    Check URL accessibility with specific TLS fingerprint
    """
    try:
        parsed = urlparse(url)
        
        # Check DNS resolution
        dns_ok = await check_dns_resolution(parsed.hostname)
        if not dns_ok:
            logger.error(f"DNS resolution failed for {parsed.hostname}")
            return False
        
        logger.info(f"DNS resolved for {parsed.hostname}")
        
        # Select TLS profile
        if not tls_profile:
            tls_profile = get_random_tls_profile()
        
        # Imitate browser TLS handshake
        response = requests.get(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            },
            impersonate=tls_profile,  # Use specific TLS fingerprint
            timeout=30
        )
        
        if response.status_code == 200:
            logger.info(f"URL {url} is accessible with TLS profile {tls_profile}")
            return True
        else:
            logger.warning(f"URL {url} returned status {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"Failed to check URL {url}: {e}")
        return False
```

## 8. Enhanced Error Handling and Retry Logic

### File: app/services/scraper_engine.py
**Change**: Add intelligent retry mechanisms

**Add to the ScraperEngine class**:

```python
async def intelligent_retry(self, url: str, scraper, filters: dict = None, max_retries: int = 3) -> list[ReviewItem]:
    """Intelligent retry with different strategies"""
    strategies = [
        ("request", self._run_request_parser),
        ("selenium", self._run_selenium_parser),
        ("browser", self._run_browser_parser),
        ("undetected", self._run_undetected_chromedriver)
    ]
    
    # Filter strategies based on scraper type
    if isinstance(scraper, (ZakupkiRequestsParser, RoseltorgParser, RtsTenderParser, NepParser)):
        # Request-based parsers
        strategy_order = ["request", "selenium", "browser", "undetected"]
    else:
        # Browser-based parsers
        strategy_order = ["undetected", "selenium", "browser", "request"]
    
    for attempt in range(max_retries):
        logger.info(f"Retry attempt {attempt + 1}/{max_retries}")
        
        for strategy_name in strategy_order:
            strategy_func = next((s[1] for s in strategies if s[0] == strategy_name), None)
            if not strategy_func:
                continue
                
            try:
                logger.info(f"Trying strategy: {strategy_name}")
                if strategy_name == "request":
                    result = strategy_func(scraper, url)
                else:
                    result = await strategy_func(scraper, url)
                    
                if result:
                    logger.info(f"Success with strategy: {strategy_name}")
                    return result
                else:
                    logger.warning(f"No results with strategy: {strategy_name}")
                    
            except Exception as e:
                logger.warning(f"Strategy {strategy_name} failed: {e}")
                continue
        
        # Wait before next retry with exponential backoff
        if attempt < max_retries - 1:
            wait_time = 2 ** attempt
            logger.info(f"Waiting {wait_time} seconds before next retry")
            await asyncio.sleep(wait_time)
    
    logger.error("All retry attempts failed")
    return []

# Add helper methods for different strategies
async def _run_request_parser(self, scraper, url: str) -> list[ReviewItem]:
    """Run request-based parser"""
    try:
        logger.info("Trying request-based parser...")
        html = scraper.fetch_html(url)
        return scraper.parse(html, url)
    except Exception as e:
        logger.error(f"Request-based parsing failed: {e}")
        return []

async def _run_undetected_chromedriver(self, scraper, url: str) -> list[ReviewItem]:
    """Run with undetected chromedriver"""
    try:
        logger.info("Trying undetected chromedriver...")
        # Implementation would go here
        # This is a simplified version
        return await self._run_selenium_parser(scraper, url)
    except Exception as e:
        logger.error(f"Undetected chromedriver failed: {e}")
        return []
```

## 9. Session and Cookie Management

### File: app/core/accounts.py
**Change**: Add session management

**Add to the AccountManager class**:

```python
class SessionManager:
    def __init__(self):
        self.sessions = {}
        self.session_locks = {}
    
    def get_session(self, account_id: str) -> dict:
        """Get or create session for account"""
        if account_id not in self.sessions:
            self.sessions[account_id] = {
                "cookies": [],
                "last_used": datetime.now(),
                "success_count": 0,
                "fail_count": 0,
                "user_agent": None
            }
            self.session_locks[account_id] = asyncio.Lock()
        return self.sessions[account_id]
    
    async def update_session_stats(self, account_id: str, success: bool):
        """Update session statistics"""
        session = self.get_session(account_id)
        if success:
            session["success_count"] += 1
        else:
            session["fail_count"] += 1
        session["last_used"] = datetime.now()
    
    def update_session_cookies(self, account_id: str, cookies: list):
        """Update session cookies"""
        session = self.get_session(account_id)
        session["cookies"] = cookies
    
    def get_session_success_rate(self, account_id: str) -> float:
        """Get session success rate"""
        session = self.get_session(account_id)
        total = session["success_count"] + session["fail_count"]
        if total == 0:
            return 1.0
        return session["success_count"] / total

# Global session manager instance
session_manager = SessionManager()
```

## Implementation Order

1. **Phase 1 - Critical Fixes**:
   - Enable stealth functionality
   - Enhance user agent rotation
   - Improve CAPTCHA detection

2. **Phase 2 - Advanced Features**:
   - Enhanced human behavior simulation
   - Proxy management system
   - TLS fingerprint rotation

3. **Phase 3 - Optimization**:
   - Intelligent retry logic
   - Session management
   - Advanced error handling

## Testing Plan

1. **Unit Tests**:
   - Test each new function individually
   - Verify stealth functionality is enabled
   - Check CAPTCHA detection improvements

2. **Integration Tests**:
   - Test full scraping workflow with enhancements
   - Verify compatibility with all supported sites
   - Check performance improvements

3. **Security Tests**:
   - Ensure no data leakage
   - Verify compliance with authorized usage
   - Check for any unintended side effects

## Expected Improvements

After implementing these changes, the system should show:

1. **Higher Success Rates**: 20-40% improvement in successful scrapes
2. **Reduced Detection**: 50%+ reduction in bot detection rates
3. **Better Reliability**: More consistent performance across sessions
4. **Enhanced Research Capabilities**: Better support for academic research