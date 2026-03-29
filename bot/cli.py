import argparse
import os
import sys

from dotenv import load_dotenv

from .client import BinanceClient, BinanceClientError
from .logging_config import setup_logger
from .orders import format_order_response, format_order_summary, place_order
from .validators import (
    ValidationError,
    validate_order_type,
    validate_price,
    validate_quantity,
    validate_side,
    validate_stop_price,
    validate_symbol,
)

load_dotenv()
logger = setup_logger("trading_bot.cli")

BANNER = r"""
  ____  _                             ____        _   
 | __ )(_)_ __   __ _ _ __   ___ ___| __ )  ___ | |_ 
 |  _ \| | '_ \ / _` | '_ \ / __/ _ \  _ \ / _ \| __|
 | |_) | | | | | (_| | | | | (_|  __/ |_) | (_) | |_ 
 |____/|_|_| |_|\__,_|_| |_|\___\___|____/ \___/ \__|
         Binance Futures Testnet Trading Bot
"""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trading-bot",
        description="Place orders on Binance Futures Testnet (USDT-M)",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("--symbol",     required=True, help="Trading pair, e.g. BTCUSDT")
    parser.add_argument("--side",       required=True, help="BUY or SELL")
    parser.add_argument("--type",       required=True, dest="order_type", help="MARKET | LIMIT | STOP_MARKET")
    parser.add_argument("--quantity",   required=True, help="Order quantity")
    parser.add_argument("--price",      default=None,  help="Limit price (required for LIMIT orders)")
    parser.add_argument("--stop-price", default=None,  dest="stop_price", help="Stop price (required for STOP_MARKET)")
    parser.add_argument("--api-key",    default=None,  help="Binance API key (or set BINANCE_API_KEY env var)")
    parser.add_argument("--api-secret", default=None,  dest="api_secret", help="Binance API secret (or set BINANCE_API_SECRET env var)")
    return parser


def run():
    print(BANNER)
    parser = build_parser()
    args = parser.parse_args()

    # ── Resolve credentials ──────────────────────────────────────────────
    api_key    = args.api_key    or os.getenv("BINANCE_API_KEY")
    api_secret = args.api_secret or os.getenv("BINANCE_API_SECRET")

    if not api_key or not api_secret:
        logger.error("API credentials missing. Provide --api-key / --api-secret or set env vars.")
        sys.exit(1)

    # ── Validate inputs ──────────────────────────────────────────────────
    try:
        symbol     = validate_symbol(args.symbol)
        side       = validate_side(args.side)
        order_type = validate_order_type(args.order_type)
        quantity   = validate_quantity(args.quantity)
        price      = validate_price(args.price, order_type)
        stop_price = validate_stop_price(args.stop_price, order_type)
    except ValidationError as exc:
        logger.error("Validation failed: %s", exc)
        print(f"\n❌  Validation error: {exc}\n")
        sys.exit(1)

    # ── Print request summary ────────────────────────────────────────────
    summary_params = {"symbol": symbol, "side": side, "type": order_type, "quantity": quantity}
    if price:
        summary_params["price"] = price
    if stop_price:
        summary_params["stopPrice"] = stop_price

    print(format_order_summary(summary_params))

    # ── Place order ──────────────────────────────────────────────────────
    client = BinanceClient(api_key, api_secret)

    try:
        response = place_order(
            client=client,
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
            stop_price=stop_price,
        )
    except BinanceClientError as exc:
        logger.error("Order failed: %s", exc)
        print(f"\n❌  Order failed — Binance error {exc.code}: {exc.message}\n")
        sys.exit(1)
    except (ConnectionError, TimeoutError) as exc:
        logger.error("Network error: %s", exc)
        print(f"\n❌  Network error: {exc}\n")
        sys.exit(1)
    except Exception as exc:
        logger.exception("Unexpected error: %s", exc)
        print(f"\n❌  Unexpected error: {exc}\n")
        sys.exit(1)

    # ── Print response ───────────────────────────────────────────────────
    print(format_order_response(response))
    print(f"\n✅  Order placed successfully! Order ID: {response.get('orderId')}\n")


if __name__ == "__main__":
    run()
