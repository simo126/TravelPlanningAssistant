"""
Calculator MCP Server
Performs arithmetic operations for agent reasoning.
"""

from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import re

app = FastAPI(title="Calculator MCP Server")

class CalculatorRequest(BaseModel):
    expression: str

class CalculatorResponse(BaseModel):
    expression: str
    result: float
    success: bool
    error: str = None

def safe_eval(expression: str) -> tuple[float, bool, str]:
    """Safely evaluate a mathematical expression"""
    try:
        # Remove spaces
        expression = expression.replace(" ", "")
        
        # Only allow numbers, operators, parentheses, and decimal points
        if not re.match(r'^[\d+\-*/().]+$', expression):
            return None, False, "Invalid characters in expression"
        
        # Evaluate
        result = eval(expression, {"__builtins__": {}}, {})
        return float(result), True, None
    except ZeroDivisionError:
        return None, False, "Division by zero"
    except Exception as e:
        return None, False, f"Calculation error: {str(e)}"

@app.get("/")
def root():
    return {"message": "Calculator MCP Server", "version": "1.0"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/tools/calculate", response_model=CalculatorResponse)
def calculate(request: CalculatorRequest) -> CalculatorResponse:
    """Perform arithmetic calculation"""
    result, success, error = safe_eval(request.expression)
    
    return CalculatorResponse(
        expression=request.expression,
        result=result if success else 0,
        success=success,
        error=error
    )

if __name__ == "__main__":
    print("🔢 Starting Calculator MCP Server on port 3337...")
    uvicorn.run(app, host="0.0.0.0", port=3337)
