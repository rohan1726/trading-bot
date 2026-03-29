# 🤖 Binance Futures Testnet Trading Bot

A clean, modular Python CLI tool to place orders on **Binance Futures Testnet (USDT-M)** with structured logging and robust error handling.

---

## 📁 Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py
│   ├── client.py          # Binance REST API client (signing, requests, errors)
│   ├── orders.py          # Order placement logic + response formatting
│   ├── validators.py      # Input validation for all CLI arguments
│   ├── logging_config.py  # Dual-output logger (file + console)
│   └── cli.py             # CLI entry point (argparse)
├── logs/                  # Auto-created; one log file per day
├── .env.example           # Template for credentials
├── requirements.txt
├── setup.py
└── README.md
```

---

## ⚙️ Setup

### 1. Get Testnet Credentials

1. Visit [Binance Futures Testnet](https://testnet.binancefuture.com)
2. Log in and go to **API Management**
3. Generate your **API Key** and **Secret Key**

### 2. Clone & Install

```bash
git clone <repo-url>
cd trading_bot

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
pip install -e .                # installs the `trading-bot` CLI command
```

### 3. Configure Credentials

**Option A — `.env` file (recommended):**

```bash
cp .env.example .env
# Edit .env and fill in your keys
```

```env
BINANCE_API_KEY=your_api_key_here
BINANCE_API_SECRET=your_api_secret_here
```

**Option B — CLI flags:**

```bash
trading-bot --api-key YOUR_KEY --api-secret YOUR_SECRET ...
```

---

## 🚀 How to Run

### Market Order (BUY)

```bash
trading-bot --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

### Market Order (SELL)

```bash
trading-bot --symbol ETHUSDT --side SELL --type MARKET --quantity 0.01
```

### Limit Order (BUY)

```bash
trading-bot --symbol BTCUSDT --side BUY --type LIMIT --quantity 0.001 --price 80000
```

### Limit Order (SELL)

```bash
trading-bot --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 86000
```

### Stop-Market Order (Bonus)

```bash
trading-bot --symbol ETHUSDT --side BUY --type STOP_MARKET --quantity 0.05 --stop-price 3100
```

---

## 📊 Sample Output

```
  ____  _                             ____        _   
 | __ )(_)_ __   __ _ _ __   ___ ___| __ )  ___ | |_ 
 ...

┌─────────────────────────────────────┐
│         ORDER REQUEST SUMMARY        │
├─────────────────────────────────────┤
│  symbol           BTCUSDT            │
│  side             BUY                │
│  type             MARKET             │
│  quantity         0.001              │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│         ORDER RESPONSE DETAILS       │
├─────────────────────────────────────┤
│  orderId          3951409541         │
│  symbol           BTCUSDT            │
│  side             BUY                │
│  type             MARKET             │
│  origQty          0.001              │
│  executedQty      0.001              │
│  avgPrice         84321.50           │
│  status           FILLED             │
└─────────────────────────────────────┘

✅  Order placed successfully! Order ID: 3951409541
```

---

## 📝 Logging

Logs are written to `logs/trading_bot_YYYYMMDD.log` automatically. Each entry captures:

- Full API request parameters (with signature)
- Raw API response body
- High-level order summary at INFO level
- Errors and exceptions with full context

Console shows **INFO and above** only; the file captures everything at **DEBUG level**.

---

## ❗ Error Handling

| Scenario | Behaviour |
|---|---|
| Missing/invalid symbol, side, type | Validation error before any API call |
| Missing price for LIMIT order | Validation error with clear message |
| Binance API error (e.g. insufficient balance) | Error code + message shown and logged |
| Network timeout / connection failure | Friendly message + logged |
| Unexpected exceptions | Full stack trace in log file |

---

## 🎁 Bonus Feature

**STOP_MARKET** orders are supported as a third order type, triggered via `--type STOP_MARKET --stop-price <price>`.

---

## ✅ Assumptions

- Only **USDT-M** (linear) futures on testnet are targeted; `BASE_URL` is hardcoded to `https://testnet.binancefuture.com`.
- `timeInForce` is set to `GTC` (Good Till Cancelled) for all LIMIT orders.
- Position side defaults to `BOTH` (one-way mode), which is the testnet default.
- Quantities and prices are passed as-is; precision rounding per symbol is left to the exchange (it will reject invalid precision with a clear error).
