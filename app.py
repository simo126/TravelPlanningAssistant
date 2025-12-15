"""
GUI Implementation (Streamlit)
Agentic Travel Planner with MCP
"""
import streamlit as st
from agent import run_travel_agent
import sys

# Page configuration
st.set_page_config(
    page_title="Agentic Travel Planner",
    page_icon="✈️",
    layout="wide"
)

# Title
st.title("✈️ Agentic Travel Planner (MCP)")

st.markdown("""
This AI agent uses:
- **Ollama** (gemma2:9b) for reasoning
- **5 MCP Servers** for external tools
- **LangChain** for agent orchestration

**Available Tools:**
- 🔍 Destination Search - Attractions & activities
- 💰 Budget Calculator - Cost estimation
- 🌤️ Weather Tool - Climate information
- 💱 Currency Converter - Multi-currency support
- 🔢 Calculator - Arithmetic operations
""")

# Sidebar with info
with st.sidebar:
    st.header("ℹ️ About")
    st.markdown("""
    This travel planning agent can:
    - Search destinations & attractions
    - Estimate travel budgets
    - Check weather conditions
    - Convert currencies
    - Perform calculations
    - Plan comprehensive itineraries
    
    **Requirements:**
    1. All 5 MCP servers running (ports 3333-3337)
    2. Ollama running with gemma2:9b model
    """)
    
    st.divider()
    
    st.header("💡 Example Queries")
    examples = [
        "Plan a 5-day trip to Barcelona with weather and budget",
        "What are the top attractions in Tokyo?",
        "Convert $1000 to Moroccan Dirhams",
        "Plan a 20-day trip to Sidi Bennour in Morocco",
        "What's the weather like in Paris?",
        "Calculate: 500*7+200"
    ]
    
    for example in examples:
        if st.button(example, key=example):
            st.session_state.query = example

# Main interface
st.divider()

# Text input
if "query" not in st.session_state:
    st.session_state.query = ""

query = st.text_input(
    "Describe your trip:",
    value=st.session_state.query,
    placeholder="e.g., Plan a 5-day trip to Barcelona with budget estimate"
)

# Plan button
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    if st.button("🚀 Plan My Trip", type="primary", use_container_width=True):
        if query:
            with st.spinner("🤔 Agent is thinking and using tools..."):
                try:
                    # Run the agent
                    output, tool_calls = run_travel_agent(query)
                    
                    # Display tool calls
                    st.divider()
                    st.subheader("🔧 Tool Calls")
                    
                    if tool_calls:
                        for call in tool_calls:
                            with st.expander(f"🛠️ Iteration {call['iteration']}: {call['tool']}", expanded=True):
                                col_a, col_b = st.columns(2)
                                with col_a:
                                    st.markdown("**Input:**")
                                    st.code(call['input'], language=None)
                                with col_b:
                                    st.markdown("**Result:**")
                                    st.info(call['result'])
                    else:
                        st.warning("No tools were called")
                    
                    # Display result
                    st.divider()
                    st.subheader("📋 Travel Plan")
                    st.write(output)
                    
                    st.success("✅ Plan generated successfully!")
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.info("""
                    **Troubleshooting:**
                    1. Make sure all 5 MCP servers are running:
                       - Port 3333: Budget Calculator
                       - Port 3334: Destination Search
                       - Port 3335: Weather Tool
                       - Port 3336: Currency Converter
                       - Port 3337: Calculator
                       
                       Or run: `start_all_servers.bat`
                       
                    2. Check if Ollama is running with gemma2:9b
                    3. Verify all server files are in the directory
                    """)
                    
                    with st.expander("Show full error"):
                        st.code(str(e))
        else:
            st.warning("⚠️ Please enter a travel request!")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: gray; font-size: 0.8em;'>
Built with LangChain, MCP, Ollama, and Streamlit | Lab 3 - Agentic AI
</div>
""", unsafe_allow_html=True)
