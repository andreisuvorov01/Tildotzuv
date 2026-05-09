import requests
import os
from typing import Optional, Dict, Any, List

class CloudflareBrowserRendering:
    """
    Класс для взаимодействия с API Cloudflare Browser Rendering.
    Поддерживает новые эндпоинты /crawl и /json.
    """

    BASE_URL = "https://api.cloudflare.com/client/v4/accounts/{account_id}/browser-rendering"

    def __init__(self, account_id: str, api_token: str):
        self.account_id = account_id
        self.api_token = api_token
        self.endpoint_url = self.BASE_URL.format(account_id=account_id)

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }

    def start_crawl(self, url: str, **kwargs) -> Dict[str, Any]:
        """
        Запускает задачу краулинга (асинхронно).
        Возвращает job_id.
        """
        payload = {"url": url}
        payload.update(kwargs)

        response = requests.post(
            f"{self.endpoint_url}/crawl",
            headers=self._get_headers(),
            json=payload
        )
        response.raise_for_status()
        return response.json()

    def get_crawl_results(self, job_id: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Получает статус или результаты задачи краулинга.
        """
        response = requests.get(
            f"{self.endpoint_url}/crawl/{job_id}",
            headers=self._get_headers(),
            params=params
        )
        response.raise_for_status()
        return response.json()

    def extract_json(self, url: str, prompt: Optional[str] = None, response_format: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """
        Извлекает структурированные данные с веб-страницы с помощью AI (синхронно).
        """
        payload = {"url": url}
        if prompt:
            payload["prompt"] = prompt
        if response_format:
            payload["response_format"] = response_format
        payload.update(kwargs)

        response = requests.post(
            f"{self.endpoint_url}/json",
            headers=self._get_headers(),
            json=payload
        )
        response.raise_for_status()
        return response.json()
