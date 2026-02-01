import json
import os
import random
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class AccountManager:
    def __init__(self, accounts_file: str = "app/accounts.json"):
        self.accounts_file = accounts_file
        self.accounts = []
        self.load_accounts()
    
    def load_accounts(self):
        """Загружает аккаунты из JSON файла."""
        if os.path.exists(self.accounts_file):
            try:
                with open(self.accounts_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.accounts = data.get("accounts", [])
                logger.info(f"Loaded {len(self.accounts)} accounts")
            except Exception as e:
                logger.error(f"Failed to load accounts: {e}")
                self.accounts = []
        else:
            logger.warning(f"Accounts file {self.accounts_file} not found. Using anonymous mode.")
            self.accounts = []

    def get_account_with_rotating_ua(self) -> Optional[Dict[str, Any]]:
        """Возвращает аккаунт со случайным User-Agent для обхода обнаружения"""
        if not self.accounts:
            return None
        
        # Выбираем случайный аккаунт
        account = random.choice(self.accounts)
        
        # Генерируем случайный User-Agent
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
        ]
        
        account_copy = account.copy()
        account_copy['user_agent'] = random.choice(user_agents)
        
        return account_copy

    def get_random_account(self) -> Optional[Dict[str, Any]]:
        """Возвращает случайный аккаунт для ротации."""
        if not self.accounts:
            return None
        return random.choice(self.accounts)

    def get_account_by_id(self, account_id: str) -> Optional[Dict[str, Any]]:
        """Возвращает аккаунт по ID."""
        for account in self.accounts:
            if account.get("id") == account_id:
                return account
        return None

    def get_all_accounts(self) -> List[Dict[str, Any]]:
        """Возвращает все аккаунты."""
        return self.accounts

    def add_account(self, account: Dict[str, Any]):
        """Добавляет новый аккаунт."""
        self.accounts.append(account)
        self.save_accounts()

    def update_account(self, account_id: str, updates: Dict[str, Any]):
        """Обновляет аккаунт по ID."""
        for i, account in enumerate(self.accounts):
            if account.get("id") == account_id:
                self.accounts[i].update(updates)
                self.save_accounts()
                return True
        return False

    def remove_account(self, account_id: str):
        """Удаляет аккаунт по ID."""
        self.accounts = [acc for acc in self.accounts if acc.get("id") != account_id]
        self.save_accounts()

    def save_accounts(self):
        """Сохраняет аккаунты в файл."""
        try:
            with open(self.accounts_file, 'w', encoding='utf-8') as f:
                json.dump({"accounts": self.accounts}, f, indent=2, ensure_ascii=False)
            logger.info("Accounts saved successfully")
        except Exception as e:
            logger.error(f"Failed to save accounts: {e}")

    def get_account_stats(self) -> Dict[str, Any]:
        """Получение статистики по аккаунтам."""
        total_accounts = len(self.accounts)
        accounts_with_proxy = sum(1 for acc in self.accounts if acc.get("proxy"))
        accounts_with_credentials = sum(1 for acc in self.accounts if acc.get("login") and acc.get("password"))
        
        return {
            "total_accounts": total_accounts,
            "accounts_with_proxy": accounts_with_proxy,
            "accounts_with_credentials": accounts_with_credentials
        }

# Глобальный экземпляр для использования в приложении
account_manager = AccountManager()