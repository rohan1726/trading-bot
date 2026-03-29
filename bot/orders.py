from typing import Any, Dict, Optional

from .client import BinanceClient
from .logging_config import setup_logger

logger = setup_logger("trading_bot.orders")


def _build_order_params(
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: Optional[float] = None,
    stop_price: Optional[float] = None,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {
        "symbol": symbol,
        "side": side,
        "type": order_type,
        "quantity": quantity,
    }

    if order_type == "LIMIT":
        params["price"] = price
        params["timeInForce"] = "GTC"

    if order_type == "STOP_MARKET":
        params["stopPrice"] = stop_price

    return params


def place_order(
    client: BinanceClient,
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: Optional[float] = None,
    stop_price: Optional[float] = None,
) -> Dict[str, Any]:
    params = _build_order_params(symbol, side, order_type, quantity, price, stop_price)

    logger.info(
        "Placing %s %s order | symbol=%s qty=%s price=%s stop=%s",
        side, order_type, symbol, quantity, price, stop_price,
    )

    response = client.place_order(**params)

    logger.info(
        "Order placed | orderId=%s status=%s executedQty=%s avgPrice=%s",
        response.get("orderId"),
        response.get("status"),
        response.get("executedQty"),
        response.get("avgPrice"),
    )

    return response


def format_order_summary(params: Dict[str, Any]) -> str:
    lines = [
        "",
        "┌─────────────────────────────────────┐",
        "│         ORDER REQUEST SUMMARY        │",
        "├─────────────────────────────────────┤",
    ]
    for key, val in params.items():
        lines.append(f"│  {key:<16} {str(val):<18} │")
    lines.append("└─────────────────────────────────────┘")
    return "\n".join(lines)


def format_order_response(response: Dict[str, Any]) -> str:
    fields = ["orderId", "symbol", "side", "type", "origQty", "executedQty", "avgPrice", "status", "timeInForce"]
    lines = [
        "",
        "┌─────────────────────────────────────┐",
        "│         ORDER RESPONSE DETAILS       │",
        "├─────────────────────────────────────┤",
    ]
    for f in fields:
        if f in response:
            lines.append(f"│  {f:<16} {str(response[f]):<18} │")
    lines.append("└─────────────────────────────────────┘")
    return "\n".join(lines)
