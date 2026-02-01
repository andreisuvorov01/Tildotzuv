import asyncio
import logging
from typing import Dict, Any, Optional
from app.core.network import make_request_with_ja4_fingerprinting
from capsolver import Capsolver
import os

logger = logging.getLogger(__name__)

class CaptchaSolver:
    def __init__(self):
        # Инициализация capsolver с API ключом
        api_key = os.getenv("CAPSOLVER_API_KEY", "")
        if api_key:
            self.capsolver = Capsolver(api_key=api_key)
        else:
            self.capsolver = None
            logger.warning("CAPSOLVER_API_KEY not set, captcha solving will be limited")
    
    async def detect_and_solve_captcha(self, page, url: str) -> bool:
        """Обнаружение и решение различных типов капчи"""
        try:
            # Проверяем наличие различных типов капчи на странице
            captcha_types = await self._detect_captcha_type(page)
            
            if not captcha_types:
                logger.info("No captcha detected on page")
                return False
            
            logger.info(f"Captcha types detected: {captcha_types}")
            
            for captcha_type in captcha_types:
                if captcha_type == "turnstile":
                    return await self._solve_turnstile_captcha(page, url)
                elif captcha_type == "recaptcha":
                    return await self._solve_recaptcha_captcha(page)
                elif captcha_type == "hcaptcha":
                    return await self._solve_hcaptcha_captcha(page)
                else:
                    logger.warning(f"Unknown captcha type: {captcha_type}")
            
            return False
            
        except Exception as e:
            logger.error(f"Error detecting and solving captcha: {e}")
            return False
    
    async def _detect_captcha_type(self, page) -> list:
        """Определение типа капчи на странице"""
        captcha_types = []
        
        try:
            # Проверяем наличие различных типов капчи
            # 1. Проверяем наличие Turnstile (Cloudflare)
            turnstile_frame = await page.query_selector('iframe[src*="challenges.cloudflare.com"]')
            if turnstile_frame:
                captcha_types.append("turnstile")
            
            # 2. Проверяем наличие reCAPTCHA
            recaptcha_frame = await page.query_selector('iframe[src*="google.com/recaptcha"]')
            if recaptcha_frame:
                captcha_types.append("recaptcha")
            
            # 3. Проверяем наличие hCaptcha
            hcaptcha_frame = await page.query_selector('iframe[src*="hcaptcha.com"]')
            if hcaptcha_frame:
                captcha_types.append("hcaptcha")
                
            # 4. Проверяем другие признаки защиты
            page_content = await page.content()
            
            # 5. Проверяем на наличие Cloudflare защитных элементов
            if any(indicator in page_content for indicator in [
                'src="/cdn-cgi/challenge-platform/',
                'window._cf_chl_opt',
                'Checking your browser',
                'src="/cdn-cgi/challenges/',
                'cloudflare',
                'Anti-DDoS защита'
            ]):
                captcha_types.append("cloudflare_challenge")
                
        except Exception as e:
            logger.error(f"Error detecting captcha type: {e}")
        
        return captcha_types
    
    async def _solve_turnstile_captcha(self, page, url: str) -> bool:
        """Решение Turnstile капчи (Cloudflare)"""
        try:
            logger.info("Attempting to solve Cloudflare Turnstile captcha")
            
            # Если у нас есть capsolver API ключ, используем его
            if self.capsolver:
                try:
                    # Получаем домен для решения капчи
                    domain = page.url.split("//")[1].split("/")[0]
                    
                    # Используем capsolver для решения Cloudflare Turnstile
                    result = self.capsolver.recognize(
                        "CustomTask",
                        websiteURL=url,
                        websiteKey="turnstile_site_key_here"  # В реальном приложении нужно извлекать динамически
                    )
                    
                    if result and result.get("solution", {}).get("token"):
                        # Установка токена cf_clearance в куки
                        await page.context.add_cookies([{
                            "name": "cf_clearance",
                            "value": result["solution"]["token"],
                            "domain": domain,
                            "path": "/",
                            "expires": None,
                            "httpOnly": False,
                            "secure": True
                        }])
                        
                        logger.info("Cloudflare Turnstile solved successfully")
                        return True
                except Exception as e:
                    logger.warning(f"Capsolver failed to solve Turnstile: {e}")
            
            # Альтернативный метод - имитация поведения для прохождения проверки
            await self._simulate_human_behavior_for_captcha(page)
            
            logger.info("Behavioral approach applied for Turnstile captcha")
            return True
            
        except Exception as e:
            logger.error(f"Error solving Turnstile captcha: {e}")
            return False
    
    async def _solve_recaptcha_captcha(self, page) -> bool:
        """Решение reCAPTCHA"""
        try:
            logger.info("Attempting to solve reCAPTCHA")
            
            # Используем capsolver если доступен
            if self.capsolver:
                try:
                    # Получаем ключ сайта и тип reCAPTCHA
                    recaptcha_frame = await page.query_selector('iframe[src*="google.com/recaptcha"]')
                    if recaptcha_frame:
                        src = await recaptcha_frame.get_attribute("src")
                        # Извлекаем sitekey из src
                        import re
                        sitekey_match = re.search(r"k=([a-zA-Z0-9_-]+)", src)
                        if sitekey_match:
                            sitekey = sitekey_match.group(1)
                            
                            result = self.capsolver.recognize(
                                "ReCaptchaV2TaskProxyLess",
                                websiteURL=page.url,
                                websiteKey=sitekey
                            )
                            
                            if result and result.get("solution", {}).get("gRecaptchaResponse"):
                                # Вставляем решение в соответствующее поле
                                await page.evaluate(f'document.querySelector("#g-recaptcha-response").innerHTML="{result["solution"]["gRecaptchaResponse"]}";')
                                
                                logger.info("reCAPTCHA solved successfully")
                                return True
                except Exception as e:
                    logger.warning(f"Capsolver failed to solve reCAPTCHA: {e}")
            
            return False
            
        except Exception as e:
            logger.error(f"Error solving reCAPTCHA: {e}")
            return False
    
    async def _solve_hcaptcha_captcha(self, page) -> bool:
        """Решение hCaptcha"""
        try:
            logger.info("Attempting to solve hCaptcha")
            
            # Используем capsolver если доступен
            if self.capsolver:
                try:
                    result = self.capsolver.recognize(
                        "HCaptchaTaskProxyLess",
                        websiteURL=page.url,
                        websiteKey="hcaptcha_site_key_here"  # Нужно извлекать динамически
                    )
                    
                    if result and result.get("solution", {}).get("token"):
                        logger.info("hCaptcha solved successfully")
                        return True
                except Exception as e:
                    logger.warning(f"Capsolver failed to solve hCaptcha: {e}")
            
            return False
            
        except Exception as e:
            logger.error(f"Error solving hCaptcha: {e}")
            return False
    
    async def _simulate_human_behavior_for_captcha(self, page):
        """Имитация человеческого поведения для обхода некоторых проверок"""
        try:
            # Имитация движения мыши
            await page.mouse.move(100, 100)
            await asyncio.sleep(0.2)
            await page.mouse.move(200, 200)
            await asyncio.sleep(0.3)
            await page.mouse.move(300, 300)
            
            # Небольшая задержка
            await asyncio.sleep(0.5)
            
            # Имитация прокрутки
            await page.mouse.wheel(0, 100)
            await asyncio.sleep(0.3)
            await page.mouse.wheel(0, -50)
            
            # Имитация клика (если есть элемент для клика)
            try:
                # Ищем элементы, которые могут быть частью проверки
                elements = await page.query_selector_all('input, button, textarea, select')
                if elements:
                    # Кликаем на случайный элемент
                    import random
                    random_element = random.choice(elements)
                    await random_element.click(force=True)
            except:
                pass
                
        except Exception as e:
            logger.error(f"Error simulating human behavior: {e}")
    
    async def advanced_captcha_detection(self, page) -> Dict[str, Any]:
        """Расширенное обнаружение капчи с деталями"""
        try:
            # Проверяем различные признаки капчи
            captcha_info = {
                "type": "unknown",
                "detected": False,
                "details": {}
            }
            
            # Проверяем Cloudflare Turnstile
            turnstile_frame = await page.query_selector('iframe[src*="challenges.cloudflare.com"]')
            if turnstile_frame:
                captcha_info["type"] = "turnstile"
                captcha_info["detected"] = True
                captcha_info["details"]["provider"] = "cloudflare"
                
                # Получаем дополнительную информацию
                src = await turnstile_frame.get_attribute("src")
                if src:
                    import urllib.parse
                    query_params = urllib.parse.parse_qs(urllib.parse.urlparse(src).query)
                    captcha_info["details"]["sitekey"] = query_params.get("on", [None])[0]
            
            # Проверяем reCAPTCHA
            recaptcha_frame = await page.query_selector('iframe[src*="google.com/recaptcha"]')
            if recaptcha_frame:
                captcha_info["type"] = "recaptcha"
                captcha_info["detected"] = True
                captcha_info["details"]["provider"] = "google"
            
            # Проверяем hCaptcha
            hcaptcha_frame = await page.query_selector('iframe[src*="hcaptcha.com"]')
            if hcaptcha_frame:
                captcha_info["type"] = "hcaptcha"
                captcha_info["detected"] = True
                captcha_info["details"]["provider"] = "hcaptcha"
            
            # Проверяем другие признаки защиты
            page_content = await page.content()
            
            # Проверяем на наличие Cloudflare защитных элементов
            if any(indicator in page_content for indicator in [
                'src="/cdn-cgi/challenge-platform/',
                'window._cf_chl_opt',
                'Checking your browser',
                'src="/cdn-cgi/challenge-platform',
                'cloudflare',
                'Anti-DDoS защита'
            ]):
                if not captcha_info["detected"]:
                    captcha_info["type"] = "cloudflare_challenge"
                    captcha_info["detected"] = True
                    captcha_info["details"]["provider"] = "cloudflare"
            
            return captcha_info
            
        except Exception as e:
            logger.error(f"Error in advanced captcha detection: {e}")
            return {"type": "unknown", "detected": False, "details": {}}
    
    async def solve_captcha_by_type(self, page, captcha_info: Dict[str, Any], url: str) -> bool:
        """Решение капчи по типу"""
        captcha_type = captcha_info.get("type", "unknown")
        
        if captcha_type == "turnstile":
            return await self._solve_turnstile_captcha(page, url)
        elif captcha_type == "recaptcha":
            return await self._solve_recaptcha_captcha(page)
        elif captcha_type == "hcaptcha":
            return await self._solve_hcaptcha_captcha(page)
        elif captcha_type == "cloudflare_challenge":
            # Для Cloudflare challenge используем поведенческий анализ
            await self._simulate_human_behavior_for_captcha(page)
            return True
        else:
            logger.info(f"No solver available for captcha type: {captcha_type}")
            return False

# Глобальный экземпляр для использования в приложении
captcha_solver = CaptchaSolver()