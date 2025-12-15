"""
Currency Converter MCP Server
Converts travel costs between different currencies.
"""

from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="Currency MCP Server")

class CurrencyRequest(BaseModel):
    amount: float
    from_currency: str
    to_currency: str

class CurrencyResponse(BaseModel):
    original_amount: float
    original_currency: str
    converted_amount: float
    converted_currency: str
    exchange_rate: float

# Mock exchange rates (base: USD)
EXCHANGE_RATES = {
    "USD": 1.0,
    "EUR": 0.92,
    "GBP": 0.79,
    "JPY": 149.50,
    "CAD": 1.35,
    "AUD": 1.52,
    "CHF": 0.88,
    "CNY": 7.24,
    "INR": 83.12,
    "MAD": 9.95,  # Moroccan Dirham
    "AED": 3.67,  # UAE Dirham
    "MXN": 17.05,
    "BRL": 4.92,
    "ZAR": 18.45,
    "SEK": 10.35,
    "NOK": 10.72,
    "DKK": 6.87,
    "SGD": 1.34,
    "HKD": 7.82,
    "KRW": 1305.50,
    "TRY": 32.15,
    "RUB": 92.50,
    "PLN": 3.95,
    "THB": 34.85
}

@app.get("/")
def root():
    return {"message": "Currency MCP Server", "version": "1.0"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/tools/convert_currency", response_model=CurrencyResponse)
def convert_currency(request: CurrencyRequest) -> CurrencyResponse:
    """Convert amount from one currency to another"""
    from_curr = request.from_currency.upper()
    to_curr = request.to_currency.upper()
    
    # Get exchange rates
    from_rate = EXCHANGE_RATES.get(from_curr, 1.0)
    to_rate = EXCHANGE_RATES.get(to_curr, 1.0)
    
    # Convert to USD first, then to target currency
    amount_in_usd = request.amount / from_rate
    converted_amount = amount_in_usd * to_rate
    
    # Calculate direct exchange rate
    exchange_rate = to_rate / from_rate
    
    return CurrencyResponse(
        original_amount=request.amount,
        original_currency=from_curr,
        converted_amount=round(converted_amount, 2),
        converted_currency=to_curr,
        exchange_rate=round(exchange_rate, 4)
    )

@app.get("/tools/supported_currencies")
def supported_currencies():
    """Get list of supported currencies"""
    return {
        "currencies": list(EXCHANGE_RATES.keys()),
        "count": len(EXCHANGE_RATES)
    }

if __name__ == "__main__":
    print("💱 Starting Currency MCP Server on port 3336...")
    uvicorn.run(app, host="0.0.0.0", port=3336)
