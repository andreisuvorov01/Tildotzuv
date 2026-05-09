import unittest
from unittest.mock import patch, MagicMock
from cloudflare_api import CloudflareBrowserRendering

class TestCloudflareBrowserRendering(unittest.TestCase):
    def setUp(self):
        self.account_id = "test_account"
        self.api_token = "test_token"
        self.cf = CloudflareBrowserRendering(self.account_id, self.api_token)

    @patch('requests.post')
    def test_start_crawl(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"success": True, "result": "job_123"}
        mock_post.return_value = mock_response

        url = "https://example.com"
        result = self.cf.start_crawl(url, limit=10)

        self.assertTrue(result["success"])
        self.assertEqual(result["result"], "job_123")

        # Проверка вызова
        expected_url = f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/browser-rendering/crawl"
        mock_post.assert_called_once_with(
            expected_url,
            headers={
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            },
            json={"url": url, "limit": 10}
        )

    @patch('requests.get')
    def test_get_crawl_results(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {"success": True, "result": {"status": "completed"}}
        mock_get.return_value = mock_response

        job_id = "job_123"
        result = self.cf.get_crawl_results(job_id, params={"limit": 1})

        self.assertEqual(result["result"]["status"], "completed")

        expected_url = f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/browser-rendering/crawl/{job_id}"
        mock_get.assert_called_once_with(
            expected_url,
            headers={
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            },
            params={"limit": 1}
        )

    @patch('requests.post')
    def test_extract_json(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"success": True, "result": {"data": "value"}}
        mock_post.return_value = mock_response

        url = "https://example.com"
        prompt = "test prompt"
        schema = {"type": "object"}

        result = self.cf.extract_json(url, prompt=prompt, response_format={"type": "json_schema", "schema": schema})

        self.assertTrue(result["success"])

        expected_url = f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/browser-rendering/json"
        mock_post.assert_called_once_with(
            expected_url,
            headers={
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            },
            json={
                "url": url,
                "prompt": prompt,
                "response_format": {"type": "json_schema", "schema": schema}
            }
        )

if __name__ == '__main__':
    unittest.main()
