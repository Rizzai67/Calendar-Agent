import streamlit as st
import os
from datetime import datetime
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.prebuilt import ToolNode, tools_condition

# Import your tools from main.py
# We'll need to refactor main.py to import the tools
from main import (
    list_calendar_event,
    current_dateTime,
    create_event,
    update_calendar_events,
    delete_calendar_event,
    tools,
    llm_with_tools,
    tool_node,
    State,
    assistant,
    app
)

# Page config
st.set_page_config(
    page_title="AI Calendar Assistant",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        background-color: #f5f7fa;
    }
    .stChatMessage {
        background-color: black;
        border-radius: 10px;
        padding: 10px;
        margin: 5px 0;
    }
    .chat-container {
        max-width: 800px;
        margin: 0 auto;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "agent_messages" not in st.session_state:
    st.session_state.agent_messages = []

# Sidebar
with st.sidebar:
    st.title("📅 Calendar Agent")
    st.markdown("---")
    
    st.subheader("Features")
    st.markdown("""
    - 📋 List upcoming events
    - ➕ Create new events
    - ✏️ Update existing events
    - 🗑️ Delete events
    - 🕐 Smart date/time parsing
    """)
    
    st.markdown("---")
    
    st.subheader("Quick Actions")
    if st.button("📋 Show Today's Events", use_container_width=True):
        st.session_state.messages.append({"role": "user", "content": "What events do I have today?"})
        st.rerun()
    
    if st.button("📅 Show This Week", use_container_width=True):
        st.session_state.messages.append({"role": "user", "content": "What events do I have this week?"})
        st.rerun()
    
    if st.button("🕐 Current Date & Time", use_container_width=True):
        st.session_state.messages.append({"role": "user", "content": "What's the current date and time?"})
        st.rerun()
    
    st.markdown("---")
    
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.agent_messages = []
        st.rerun()
    
    st.markdown("---")
    st.caption("Built with LangGraph + Groq + Streamlit")

# Main chat interface
st.title("🤖 AI Calendar Assistant")
st.markdown("Ask me anything about your calendar!")

# Chat container
chat_container = st.container()

with chat_container:
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask about your calendar..."):
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Show assistant thinking
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # Prepare input for the agent
            inputs = {"messages": [("user", prompt)]}
            
            # Stream the agent's response
            response_text = ""
            tool_calls_made = []
            
            try:
                for output in app.stream(inputs, stream_mode="updates"):
                    for key, value in output.items():
                        last_msg = value["messages"][-1]
                        
                        # Check if tools were called
                        if hasattr(last_msg, 'tool_calls') and last_msg.tool_calls:
                            for tool_call in last_msg.tool_calls:
                                tool_calls_made.append(tool_call['name'])
                        
                        # Get the final assistant response
                        elif last_msg.content:
                            response_text = last_msg.content
                
                # Display tool calls if any
                if tool_calls_made:
                    with st.expander("🔧 Tools Used", expanded=False):
                        for tool in tool_calls_made:
                            st.caption(f"• {tool}")
                
                # Display the response
                st.markdown(response_text)
                
                # Add assistant response to chat
                st.session_state.messages.append({"role": "assistant", "content": response_text})
            
            except Exception as e:
                error_msg = f"❌ Error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

# Example prompts at the bottom
if len(st.session_state.messages) == 0:
    st.markdown("---")
    st.subheader("💡 Try asking:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("📋 'What events do I have tomorrow?'")
        st.info("➕ 'Schedule a meeting tomorrow at 2 PM'")
    
    with col2:
        st.info("✏️ 'Update Team Standup to start at 3 PM'")
        st.info("🗑️ 'Delete the dentist appointment'")