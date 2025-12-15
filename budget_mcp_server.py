"""
Budget Calculator MCP Server
This is a proper FastAPI implementation following MCP principles.
"""
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="Budget Calculator MCP")

# Request/Response models
class BudgetRequest(BaseModel):
    destination: str
    days: int

class BudgetResponse(BaseModel):
    destination: str
    days: int
    estimated_budget: float

# MCP Tool endpoint
@app.post("/tools/estimate_budget", response_model=BudgetResponse)
def estimate_budget(request: BudgetRequest) -> BudgetResponse:
    """Estimate travel budget in USD."""
    base_cost = 200
    total = base_cost * request.days
    
    return BudgetResponse(
        destination=request.destination,
        days=request.days,
        estimated_budget=total
    )

# Health check endpoint (standard for MCP servers)
@app.get("/health")
def health():
    return {"status": "healthy", "service": "budget-tools"}

# Root endpoint with server info
@app.get("/")
def root():
    return {
        "service": "budget-tools",
        "version": "1.0",
        "endpoints": {
            "estimate_budget": "/tools/estimate_budget",
            "health": "/health"
        }
    }

if __name__ == "__main__":
    print("Starting Budget Calculator MCP Server on port 3333...")
    uvicorn.run(app, host="0.0.0.0", port=3333)