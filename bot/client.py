import hashlib
import hmac
import time
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import requests

from .logging_config import setup_logger

BASE_URL = "https://testnet.binancefuture.com"
logger = setup_logger("trading_bot.client")


class BinanceClientError(Exception):
    """Raised when Binance API returns an error response."""
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(f"Binance API Error {code}: {message}")


class BinanceClient:
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.session = requests.Session()
        self.session.headers.update({"X-MBX-APIKEY": self.api_key})

    # ------------------------------------------------------------------ #
    #  Internal helpers                                                    #
    # ------------------------------------------------------------------ #

    def _sign(self, params: Dict[str, Any]) -> Dict[str, Any]:
        params["timestamp"] = int(time.time() * 1000)
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        params["signature"] = signature
        return params

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        signed: bool = False,
    ) -> Dict[str, Any]:
        url = BASE_URL + endpoint
        params = params or {}

        if signed:
            params = self._sign(params)

        logger.debug("REQUEST  %s %s | params=%s", method.upper(), endpoint, params)

        try:
            response = self.session.request(method, url, params=params, timeout=10)
        except requests.exceptions.ConnectionError as exc:
            logger.error("Network error connecting to Binance: %s", exc)
            raise ConnectionError(f"Network error: {exc}") from exc
        except requests.exceptions.Timeout:
            logger.error("Request timed out for %s", url)
            raise TimeoutError("Request to Binance timed out.")

        logger.debug("RESPONSE %s %s | status=%s body=%s", method.upper(), endpoint, response.status_code, response.text)

        try:
            data = response.json()
        except ValueError:
            logger.error("Non-JSON response: %s", response.text)
            raise ValueError(f"Unexpected non-JSON response: {response.text}")

        if isinstance(data, dict) and "code" in data and data["code"] != 200:
            logger.error("API error | code=%s msg=%s", data.get("code"), data.get("msg"))
            raise BinanceClientError(data["code"], data.get("msg", "Unknown error"))

        return data

    # ------------------------------------------------------------------ #
    #  Public API methods                                                  #
    # ------------------------------------------------------------------ #

    def get_server_time(self) -> int:
        data = self._request("GET", "/fapi/v1/time")
        return data["serverTime"]

    def get_exchange_info(self, symbol: str) -> Dict[str, Any]:
        return self._request("GET", "/fapi/v1/exchangeInfo", params={"symbol": symbol})

    def place_order(self, **kwargs) -> Dict[str, Any]:
        return self._request("POST", "/fapi/v1/order", params=kwargs, signed=True)

    def get_order(self, symbol: str, order_id: int) -> Dict[str, Any]:
        return self._request(
            "GET", "/fapi/v1/order", params={"symbol": symbol, "orderId": order_id}, signed=True
        )
