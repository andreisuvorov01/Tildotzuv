import asyncio
import random
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

async def human_scroll(page, distance: int = 1000):
    """Эмуляция человеческого скроллинга"""
    try:
        # Скроллим небольшими частями с задержками
        scroll_step = distance // 5
        for _ in range(5):
            await page.evaluate(f"window.scrollBy(0, {scroll_step})")
            await asyncio.sleep(random.uniform(0.1, 0.3))
    except Exception as e:
        logger.warning(f"Human scroll failed: {e}")

async def human_mouse_move(page, start_x: int, start_y: int, end_x: int, end_y: int):
    """Эмуляция движения мыши"""
    try:
        await page.mouse.move(start_x, start_y)
        await asyncio.sleep(random.uniform(0.1, 0.2))
        await page.mouse.move(end_x, end_y)
    except Exception as e:
        logger.warning(f"Human mouse move failed: {e}")

async def login_to_avito(page, login: str, password: str) -> bool:
    """Простая попытка логина на Avito"""
    try:
        # Переходим на страницу входа
        await page.goto("https://m.avito.ru/profile/login")
        await asyncio.sleep(2)
        
        # Ищем поля ввода
        login_field = await page.query_selector("input[type='email'], input[name='login']")
        password_field = await page.query_selector("input[type='password']")
        
        if login_field and password_field:
            await login_field.fill(login)
            await password_field.fill(password)
            
            # Ищем кнопку входа
            submit_btn = await page.query_selector("button[type='submit'], .js-submit-button")
            if submit_btn:
                await submit_btn.click()
                await asyncio.sleep(3)
                return True
                
        return False
    except Exception as e:
        logger.error(f"Login failed: {e}")
        return False

def realistic_mouse_movement(start_x: int, start_y: int, end_x: int, end_y: int, steps: int = 50) -> List[Dict[str, int]]:
    """
    Generate realistic mouse movement coordinates using Bezier curves
    """
    points = []
    
    # Generate control points for Bezier curve
    ctrl_x1 = start_x + (end_x - start_x) * random.uniform(0.2, 0.4)
    ctrl_y1 = start_y + (end_y - start_y) * random.uniform(0.2, 0.4)
    ctrl_x2 = start_x + (end_x - start_x) * random.uniform(0.6, 0.8)
    ctrl_y2 = start_y + (end_y - start_y) * random.uniform(0.6, 0.8)
    
    # Calculate points along the Bezier curve
    for i in range(steps + 1):
        t = i / steps
        x = (1 - t)**3 * start_x + 3 * (1 - t)**2 * t * ctrl_x1 + 3 * (1 - t) * t**2 * ctrl_x2 + t**3 * end_x
        y = (1 - t)**3 * start_y + 3 * (1 - t)**2 * t * ctrl_y1 + 3 * (1 - t) * t**2 * ctrl_y2 + t**3 * end_y
        points.append({"x": round(x), "y": round(y)})
    
    return points

async def human_typing(page, selector: str, text: str, min_delay: float = 0.05, max_delay: float = 0.2):
    """
    Simulate human typing with variable delays and potential typos
    """
    try:
        element = await page.query_selector(selector)
        if not element:
            raise Exception(f"Element not found: {selector}")
        
        # Focus on the element
        await element.focus()
        
        # Type each character with random delays
        for char in text:
            await page.keyboard.type(char)
            # Random delay between keystrokes
            await asyncio.sleep(random.uniform(min_delay, max_delay))
            
            # Occasionally make and correct typos
            if random.random() < 0.05:  # 5% chance of typo
                typo_char = random.choice("abcdefghijklmnopqrstuvwxyz")
                await page.keyboard.type(typo_char)
                await asyncio.sleep(random.uniform(0.1, 0.3))
                await page.keyboard.press("Backspace")
                await asyncio.sleep(random.uniform(0.1, 0.2))
                await page.keyboard.type(char)
                await asyncio.sleep(random.uniform(min_delay, max_delay))
                
    except Exception as e:
        logger.warning(f"Human typing failed: {e}")

def generate_human_reading_time(text: str) -> float:
    """
    Generate realistic reading time based on text length
    """
    words = len(text.split())
    # Average reading speed: 200-250 words per minute
    reading_speed = random.uniform(200, 250)
    return (words / reading_speed) * 60

async def human_pause(min_seconds: float = 1.0, max_seconds: float = 5.0):
    """
    Generate human-like pauses
    """
    pause_duration = random.uniform(min_seconds, max_seconds)
    await asyncio.sleep(pause_duration)