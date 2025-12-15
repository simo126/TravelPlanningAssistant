"""
Step 4: Creating the LangChain Agent
Following the lab structure with Ollama instead of OpenAI.
"""
from langchain_community.llms import Ollama
from mcp_connector import MCPToolkit
import re

# Initialize LLM (using Ollama instead of ChatOpenAI)
print("Initializing LLM...")
llm = Ollama(
    model="gemma2:9b",
    temperature=0.7,
    base_url="http://localhost:11434"
)

# Connect to all MCP servers and get tools
print("Connecting to MCP servers...")
mcp_toolkit = MCPToolkit.from_servers({
    "budget": "http://localhost:3333",
    "search": "http://localhost:3334",
    "weather": "http://localhost:3335",
    "currency": "http://localhost:3336",
    "calculator": "http://localhost:3337"
})
tools = mcp_toolkit.get_tools()

if not tools:
    print("Error: No tools discovered. Make sure all MCP servers are running!")
    exit(1)

print(f"Loaded {len(tools)} tool(s): {[t.name for t in tools]}")

# Enhanced agent prompt for autonomous decision-making
prompt = """
You are a travel planning agent that MUST use ALL AVAILABLE TOOLS for every request.

MANDATORY: You MUST call ALL 5 tools before providing your final answer:
1. search_destination - Get attractions and activities
2. estimate_budget - Calculate trip cost
3. get_weather - Check weather conditions
4. convert_currency - Convert budget to another currency (use EUR or MAD)
5. calculate - Do arithmetic (e.g., calculate per-day cost)

TOOL USAGE FORMAT (EXACT format required):
ACTION: tool_name
INPUT: tool_input

EXAMPLE for "Plan a 5-day trip to Barcelona":

ACTION: search_destination
INPUT: Barcelona

[wait for result]

ACTION: estimate_budget
INPUT: Barcelona,5

[wait for result]

ACTION: get_weather
INPUT: Barcelona

[wait for result]

ACTION: convert_currency
INPUT: 1000,USD,EUR

[wait for result]

ACTION: calculate
INPUT: 1000/5

[wait for result]

FINAL ANSWER: [Complete plan using ALL tool results]

REMEMBER: You MUST use ALL 5 tools. Do not skip any tool.
"""

# Create ReAct agent (custom implementation compatible with the lab structure)
class ReactAgent:
    """ReAct agent that follows the lab's agent structure."""
    
    def __init__(self, llm, tools, prompt):
        self.llm = llm
        self.tools = {tool.name: tool for tool in tools}
        self.system_prompt = prompt
        self.max_iterations = 15
    
    def _suggest_next_tool(self, tools_used, required_tools, user_request):
        """Suggest the next tool to call based on what's been used"""
        # Preferred order
        order = ["search_destination", "estimate_budget", "get_weather", "convert_currency", "calculate"]
        
        for tool in order:
            if tool in required_tools:
                return tool
        
        # Fallback to any remaining
        return list(required_tools)[0] if required_tools else None
    
    def invoke(self, input_dict):
        """
        Invoke the agent with user input.
        Follows the same interface as the lab: agent.invoke({"input": user_request})
        Returns: {"input": query, "output": result, "tool_calls": [...]}
        """
        user_request = input_dict.get("input", "")
        
        print(f"\n{'='*60}")
        print(f"User Request: {user_request}")
        print(f"{'='*60}\n")
        
        # Track tool usage
        tools_used = []
        tool_results = {}
        tool_calls_log = []  # For GUI display
        required_tools = set(self.tools.keys())  # All tools must be called
        
        # Build tool descriptions
        tool_desc = "\n".join([f"- {name}: {tool.description}" for name, tool in self.tools.items()])
        
        # Create full prompt with ordered tool sequence
        full_prompt = f"""{self.system_prompt}

Available tools:
{tool_desc}

User question: {user_request}

MANDATORY SEQUENCE - Call tools in this order:
1. search_destination - First
2. estimate_budget - Second  
3. get_weather - Third
4. convert_currency - Fourth
5. calculate - Fifth (then FINAL ANSWER)

Start NOW with search_destination:
ACTION: search_destination
INPUT:"""

        # ReAct loop
        for iteration in range(self.max_iterations):
            print(f"\n--- Iteration {iteration + 1} ---")
            
            # Get LLM response
            response = self.llm.invoke(full_prompt)
            print(f"Agent thinking: {response[:200]}...\n")
            
            # Check if final answer reached
            if "FINAL ANSWER:" in response:
                final = response.split("FINAL ANSWER:")[1].strip()
                print(f"\n{'='*60}")
                print("Agent reached final answer!")
                print(f"{'='*60}\n")
                return {"input": user_request, "output": final, "tool_calls": tool_calls_log}
            
            # Check if tool action requested
            if "ACTION:" in response and "INPUT:" in response:
                try:
                    action = re.search(r'ACTION:\s*(\w+)', response, re.IGNORECASE).group(1)
                    input_match = re.search(r'INPUT:\s*(.+?)(?=\n|FINAL|$)', response, re.DOTALL | re.IGNORECASE)
                    tool_input = input_match.group(1).strip() if input_match else ""
                    
                    # Clean up tool input
                    tool_input = tool_input.strip('` \n\'"')
                    
                    if action in self.tools:
                        # Check if tool was already called
                        if action not in required_tools:
                            full_prompt += f"\n\nError: You already called '{action}'. You cannot call the same tool twice.\nRemaining tools: {', '.join(required_tools)}\n\nCall a DIFFERENT tool now:"
                            continue
                        
                        print(f"🔧 Calling tool: {action}")
                        print(f"📥 Input: {tool_input}")
                        result = self.tools[action].run(tool_input)
                        print(f"📤 Result: {result}\n")
                        
                        tools_used.append(action)
                        tool_results[action] = result
                        required_tools.discard(action)
                        
                        # Log for GUI
                        tool_calls_log.append({
                            "iteration": iteration + 1,
                            "tool": action,
                            "input": tool_input,
                            "result": result
                        })
                        
                        # Check if all tools have been called
                        if len(required_tools) == 0:
                            # Build summary of all tool results
                            summary = "\n".join([f"{tool}: {res}" for tool, res in tool_results.items()])
                            full_prompt += f"\n\nObservation: {result}\n\n✅ EXCELLENT! You have used ALL 5 required tools.\n\nALL TOOL RESULTS:\n{summary}\n\nNow you MUST provide your FINAL ANSWER using ONLY the actual data above. DO NOT use placeholders.\n\nFINAL ANSWER:"
                        else:
                            # Suggest next tool from remaining
                            next_tool = self._suggest_next_tool(tools_used, required_tools, user_request)
                            remaining = ", ".join(required_tools)
                            full_prompt += f"\n\nObservation: {result}\n\n✅ Good! Remaining tools: {remaining}\n\nNow call '{next_tool}' next:\nACTION: {next_tool}\nINPUT:"
                    else:
                        full_prompt += f"\n\nError: Unknown tool '{action}'. Available: {', '.join(self.tools.keys())}\nTry again with a valid tool."
                except Exception as e:
                    print(f"❌ Error: {e}")
                    full_prompt += f"\n\nError parsing. You must use this exact format:\nACTION: tool_name\nINPUT: value\n\nTry again."
            else:
                # Agent didn't use ACTION format - check if it's providing FINAL ANSWER
                if "FINAL ANSWER" not in response.upper() and len(required_tools) > 0:
                    remaining = ", ".join(required_tools)
                    full_prompt += f"\n\nYour response: {response}\n\nERROR: You have NOT called all tools yet. Missing: {remaining}\n\nYou MUST call a tool using:\nACTION: tool_name\nINPUT: value\n\nCall the next required tool now:"
                elif len(required_tools) == 0:
                    # All tools called, accept as answer even without FINAL ANSWER prefix
                    print("Agent provided answer after using all tools.")
                    return {"input": user_request, "output": response, "tool_calls": tool_calls_log}
                else:
                    full_prompt += f"\n\n{response}\n\nNow call the next required tool."
        
        # If we have tool results, create a summary
        if tool_results:
            summary = "Based on the tools used:\n"
            for tool, result in tool_results.items():
                summary += f"\n{tool}: {result}\n"
            return {"input": user_request, "output": f"Could not generate complete answer in time, but gathered:\n{summary}", "tool_calls": tool_calls_log}
        
        return {"input": user_request, "output": "Could not complete within iteration limit.", "tool_calls": tool_calls_log}

# Create agent
agent = ReactAgent(
    llm=llm,
    tools=tools,
    prompt=prompt
)

# Step 5: Agent Execution
def run_travel_agent(user_request: str):
    """Run the travel agent with a user request. Returns (output, tool_calls)"""
    response = agent.invoke({"input": user_request})
    return response.get("output", ""), response.get("tool_calls", [])

# Test the agent
if __name__ == "__main__":
    print("\n" + "="*60)
    print("Travel Planning Agent Ready!")
    print("="*60)
    
    # Example queries
    queries = [
        "Plan a 5-day trip to Barcelona. I need a budget estimate.",
        "How much would a 3-day trip to Barcelona cost?"
    ]
    
    # Run first query
    query = queries[0]
    print(f"\nTesting with: {query}\n")
    
    try:
        result = run_travel_agent(query)
        print("\n" + "="*60)
        print("FINAL RESULT:")
        print("="*60)
        print(result)
    except Exception as e:
        print(f"\nError: {e}")
        print("\nMake sure:")
        print("1. Budget MCP server is running (python budget_mcp_server.py)")
        print("2. Ollama is running and has gemma2:9b model")
        import traceback
        traceback.print_exc()
