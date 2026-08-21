#!/usr/bin/env python3
"""
Testes para resiliência de rede (retry com backoff) em _tipos_comuns.py.
Usa mock para simular falhas transitórias e sucesso.
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock
from urllib.error import HTTPError, URLError

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from _tipos_comuns import http_get_with_retry


class TestHttpRetry(unittest.TestCase):
    """Testes de retry com backoff exponencial."""

    def test_sucesso_primeira_tentativa(self):
        """Sucesso na primeira tentativa — sem retry."""
        with patch('_tipos_comuns.urlopen') as mock_urlopen:
            mock_response = MagicMock()
            mock_response.read.return_value = b"sucesso"
            mock_urlopen.return_value = mock_response

            result = http_get_with_retry("http://test.example.com/api")
            self.assertEqual(result, b"sucesso")
            mock_urlopen.assert_called_once()

    def test_retry_em_503_transitorio(self):
        """Falha com 503 (transitório) na primeira, sucesso na segunda."""
        with patch('_tipos_comuns.urlopen') as mock_urlopen:
            mock_response = MagicMock()
            mock_response.read.return_value = b"sucesso segunda"

            # Primeira tentativa: HTTPError 503
            http_error = HTTPError(
                url="http://test.example.com",
                code=503,
                msg="Service Unavailable",
                hdrs={},
                fp=None
            )
            mock_urlopen.side_effect = [http_error, mock_response]

            result = http_get_with_retry("http://test.example.com/api", max_retries=3)
            self.assertEqual(result, b"sucesso segunda")
            self.assertEqual(mock_urlopen.call_count, 2)

    def test_falha_404_nao_retenta(self):
        """HTTPError 404 (não-transitório) — falha imediatamente sem retry."""
        with patch('_tipos_comuns.urlopen') as mock_urlopen:
            http_error = HTTPError(
                url="http://test.example.com",
                code=404,
                msg="Not Found",
                hdrs={},
                fp=None
            )
            mock_urlopen.side_effect = http_error

            with self.assertRaises(HTTPError) as context:
                http_get_with_retry("http://test.example.com/api", max_retries=3)

            self.assertEqual(context.exception.code, 404)
            mock_urlopen.assert_called_once()  # Sem retries

    def test_retry_em_429_rate_limit(self):
        """Falha com 429 (Too Many Requests) — transitório, retentar."""
        with patch('_tipos_comuns.urlopen') as mock_urlopen:
            mock_response = MagicMock()
            mock_response.read.return_value = b"sucesso retry"

            http_error = HTTPError(
                url="http://test.example.com",
                code=429,
                msg="Too Many Requests",
                hdrs={},
                fp=None
            )
            mock_urlopen.side_effect = [http_error, mock_response]

            result = http_get_with_retry("http://test.example.com/api", max_retries=3)
            self.assertEqual(result, b"sucesso retry")
            self.assertEqual(mock_urlopen.call_count, 2)

    def test_timeout_retentar(self):
        """URLError de timeout — retentar."""
        with patch('_tipos_comuns.urlopen') as mock_urlopen:
            mock_response = MagicMock()
            mock_response.read.return_value = b"sucesso apos timeout"

            timeout_error = URLError("Connection timed out")
            mock_urlopen.side_effect = [timeout_error, mock_response]

            result = http_get_with_retry("http://test.example.com/api", max_retries=3)
            self.assertEqual(result, b"sucesso apos timeout")
            self.assertEqual(mock_urlopen.call_count, 2)

    def test_max_retries_esgotados(self):
        """Máximo de retries atingido — falha."""
        with patch('_tipos_comuns.urlopen') as mock_urlopen:
            http_error = HTTPError(
                url="http://test.example.com",
                code=503,
                msg="Service Unavailable",
                hdrs={},
                fp=None
            )
            mock_urlopen.side_effect = http_error

            with self.assertRaises(HTTPError):
                http_get_with_retry("http://test.example.com/api", max_retries=2)

            self.assertEqual(mock_urlopen.call_count, 2)

    def test_403_nao_retenta(self):
        """HTTPError 403 (Forbidden) — não-retentável."""
        with patch('_tipos_comuns.urlopen') as mock_urlopen:
            http_error = HTTPError(
                url="http://test.example.com",
                code=403,
                msg="Forbidden",
                hdrs={},
                fp=None
            )
            mock_urlopen.side_effect = http_error

            with self.assertRaises(HTTPError):
                http_get_with_retry("http://test.example.com/api", max_retries=3)

            mock_urlopen.assert_called_once()  # Sem retries


class TestPlaywrightRetry(unittest.TestCase):
    """Testes de retry para Playwright page.goto()."""

    def test_goto_sucesso_primeira(self):
        """page.goto() sucesso na primeira."""
        mock_page = MagicMock()
        mock_response = MagicMock()
        mock_page.goto.return_value = mock_response

        from _tipos_comuns import playwright_goto_with_retry
        result = playwright_goto_with_retry(mock_page, "http://test.example.com")

        self.assertEqual(result, mock_response)
        mock_page.goto.assert_called_once()

    def test_goto_retry_em_timeout(self):
        """page.goto() timeout na primeira, sucesso na segunda."""
        mock_page = MagicMock()
        mock_response = MagicMock()

        timeout_error = TimeoutError("Connection timeout")
        mock_page.goto.side_effect = [timeout_error, mock_response]

        from _tipos_comuns import playwright_goto_with_retry
        result = playwright_goto_with_retry(mock_page, "http://test.example.com", max_retries=3)

        self.assertEqual(result, mock_response)
        self.assertEqual(mock_page.goto.call_count, 2)

    def test_goto_max_retries_timeout(self):
        """page.goto() timeout em todos os retries."""
        mock_page = MagicMock()
        timeout_error = TimeoutError("Connection timeout")
        mock_page.goto.side_effect = timeout_error

        from _tipos_comuns import playwright_goto_with_retry
        with self.assertRaises(TimeoutError):
            playwright_goto_with_retry(mock_page, "http://test.example.com", max_retries=2)

        self.assertEqual(mock_page.goto.call_count, 2)

    def test_goto_erro_nao_transitorio(self):
        """page.goto() erro não-transitório — falha imediatamente."""
        mock_page = MagicMock()
        other_error = Exception("Invalid argument")
        mock_page.goto.side_effect = other_error

        from _tipos_comuns import playwright_goto_with_retry
        with self.assertRaises(Exception):
            playwright_goto_with_retry(mock_page, "http://test.example.com", max_retries=3)

        mock_page.goto.assert_called_once()  # Sem retries


if __name__ == "__main__":
    unittest.main()
