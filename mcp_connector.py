"""
Connecting LangChain to MCP
This module creates LangChain tools that connect to MCP servers via HTTP.
"""
import requests
from langchain_core.tools import tool
from typing import List

class MCPToolkit:
    """Toolkit to connect LangChain agents to multiple MCP servers."""
    
    def __init__(self, server_urls: dict):
        """
        Initialize with dictionary of server_name: server_url
        Example: {"budget": "http://localhost:3333", "weather": "http://localhost:3335"}
        """
        self.server_urls = {k: v.rstrip('/') for k, v in server_urls.items()}
        self.tools = []
    
    @classmethod
    def from_servers(cls, server_urls: dict):
        """Create toolkit from multiple MCP server URLs."""
        toolkit = cls(server_urls)
        toolkit._discover_tools()
        return toolkit
    
    def _discover_tools(self):
        """Discover available tools from all MCP servers."""
        # Connect to each server and create tools
        for server_name, server_url in self.server_urls.items():
            try:
                health_response = requests.get(f"{server_url}/health", timeout=2)
                if health_response.status_code == 200:
                    print(f"✓ Connected to {server_name} MCP server at {server_url}")
                else:
                    print(f"Warning: {server_name} server at {server_url} is not healthy")
                    continue
            except requests.exceptions.RequestException as e:
                print(f"✗ Failed to connect to {server_name} server at {server_url}: {e}")
                continue
        
        # Create all tools
        if "budget" in self.server_urls:
            self.tools.append(self._create_budget_tool())
        if "search" in self.server_urls:
            self.tools.append(self._create_search_tool())
        if "weather" in self.server_urls:
            self.tools.append(self._create_weather_tool())
        if "currency" in self.server_urls:
            self.tools.append(self._create_currency_tool())
        if "calculator" in self.server_urls:
            self.tools.append(self._create_calculator_tool())
    
    def _create_budget_tool(self):
        """Create LangChain tool for budget estimation."""
        server_url = self.server_urls["budget"]
        
        @tool
        def estimate_budget(input_str: str) -> str:
            """Estimates travel budget. Input: 'destination,days' (e.g., 'Barcelona,5')"""
            try:
                parts = input_str.split(',')
                if len(parts) != 2:
                    return "Error: Use format 'destination,days'"
                
                destination = parts[0].strip()
                days = int(parts[1].strip())
                
                response = requests.post(
                    f"{server_url}/tools/estimate_budget",
                    json={"destination": destination, "days": days},
                    timeout=5
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return f"Budget: ${data['estimated_budget']:.2f} USD for {data['days']} days in {data['destination']}"
                return f"Error: Status {response.status_code}"
            except Exception as e:
                return f"Error: {str(e)}"
        
        return estimate_budget
    
    def _create_search_tool(self):
        """Create LangChain tool for destination search."""
        server_url = self.server_urls["search"]
        
        @tool
        def search_destination(destination: str) -> str:
            """Search for attractions, activities, and landmarks in a destination. Input: destination name"""
            try:
                response = requests.post(
                    f"{server_url}/tools/search_destination",
                    json={"destination": destination},
                    timeout=5
                )
                
                if response.status_code == 200:
                    data = response.json()
                    result = f"Destination: {data['destination']}\n\n"
                    result += f"🎯 Top Attractions:\n"
                    for attr in data['attractions'][:5]:
                        result += f"  • {attr}\n"
                    result += f"\n🎨 Activities:\n"
                    for act in data['activities'][:5]:
                        result += f"  • {act}\n"
                    result += f"\n🏛️ Landmarks:\n"
                    for lm in data['landmarks'][:3]:
                        result += f"  • {lm}\n"
                    return result
                return f"Error: Status {response.status_code}"
            except Exception as e:
                return f"Error: {str(e)}"
        
        return search_destination
    
    def _create_weather_tool(self):
        """Create LangChain tool for weather information."""
        server_url = self.server_urls["weather"]
        
        @tool
        def get_weather(input_str: str) -> str:
            """Get weather info for a destination. Input: destination name (or 'destination,YYYY-MM-DD')"""
            try:
                parts = input_str.split(',')
                destination = parts[0].strip()
                date = parts[1].strip() if len(parts) > 1 else None
                
                response = requests.post(
                    f"{server_url}/tools/get_weather",
                    json={"destination": destination, "date": date},
                    timeout=5
                )
                
                if response.status_code == 200:
                    data = response.json()
                    result = f"Weather for {data['destination']}:\n"
                    result += f"Temperature: {data['temperature']}\n"
                    result += f"Conditions: {data['conditions']}\n"
                    result += f"Recommendation: {data['recommendation']}"
                    return result
                return f"Error: Status {response.status_code}"
            except Exception as e:
                return f"Error: {str(e)}"
        
        return get_weather
    
    def _create_currency_tool(self):
        """Create LangChain tool for currency conversion."""
        server_url = self.server_urls["currency"]
        
        @tool
        def convert_currency(input_str: str) -> str:
            """Convert currency. Input: 'amount,from_currency,to_currency' (e.g., '1000,USD,EUR')"""
            try:
                parts = input_str.split(',')
                if len(parts) != 3:
                    return "Error: Use format 'amount,from_currency,to_currency'"
                
                amount = float(parts[0].strip())
                from_curr = parts[1].strip().upper()
                to_curr = parts[2].strip().upper()
                
                response = requests.post(
                    f"{server_url}/tools/convert_currency",
                    json={"amount": amount, "from_currency": from_curr, "to_currency": to_curr},
                    timeout=5
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return f"{data['original_amount']} {data['original_currency']} = {data['converted_amount']} {data['converted_currency']} (rate: {data['exchange_rate']})"
                return f"Error: Status {response.status_code}"
            except Exception as e:
                return f"Error: {str(e)}"
        
        return convert_currency
    
    def _create_calculator_tool(self):
        """Create LangChain tool for calculations."""
        server_url = self.server_urls["calculator"]
        
        @tool
        def calculate(expression: str) -> str:
            """Perform arithmetic calculation. Input: mathematical expression (e.g., '100*5+200')"""
            try:
                response = requests.post(
                    f"{server_url}/tools/calculate",
                    json={"expression": expression},
                    timeout=5
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data['success']:
                        return f"{data['expression']} = {data['result']}"
                    return f"Error: {data['error']}"
                return f"Error: Status {response.status_code}"
            except Exception as e:
                return f"Error: {str(e)}"
        
        return calculate
    
    def get_tools(self):
        """Get list of LangChain tools."""
        return self.tools


# Example usage
if __name__ == "__main__":
    # Connect to MCP server
    mcp_toolkit = MCPToolkit.from_server(
        server_url="http://localhost:3333"
    )
    
    # Get tools
    tools = mcp_toolkit.get_tools()
    
    print(f"\nDiscovered {len(tools)} tool(s):")
    for tool in tools:
        print(f"  - {tool.name}: {tool.description}")
    
    # Test the tool
    if tools:
        print("\nTesting tool...")
        result = tools[0].run("Barcelona,5")
        print(f"Result:\n{result}")
