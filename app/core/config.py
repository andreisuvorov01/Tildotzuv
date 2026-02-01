from pydantic_settings import BaseSettings
from typing import Optional, List


class Settings(BaseSettings):
    # Формат прокси: http://user:pass@ip:port
    PROXY_URL: Optional[str] = None
    
    # Список прокси для ротации
    PROXY_LIST: Optional[List[str]] = None
    
    # Интервал ротации прокси (в минутах)
    PROXY_ROTATION_INTERVAL: int = 30

    # Настройки браузера
    HEADLESS: bool = True
    
    # Настройки сессий
    SESSION_TIMEOUT_HOURS: int = 24

    class Config:
        env_file = ".env"


settings = Settings()
