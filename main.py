#%%
import os
from typing import Annotated
from typing_extensions import TypedDict
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.tools import tool
from datetime import datetime, timezone
from langgraph.prebuilt import ToolNode, tools_condition
#%%
# 1. SETUP ENVIRONMENT
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

# 2. STATE DEFINITION
class State(TypedDict):
    messages: Annotated[list, add_messages]

# 3. INITIALIZE LLM
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    groq_api_key=api_key,
    model_kwargs={
        'tool_choice':'auto'
    }
)

# 4. TOOLS DEFINITION
from auth_test import get_calendar_service
#%%
@tool
def list_calendar_event(max_results: int = 5):
    """
    Fetch the next upcoming events from the user's google calendar. and know what date today is.
    Use this whenever the user asks about their time, availability, or schedule.
    
    Args: 
        max_results: Maximum number of events to retrieve (default:5)
    Returns:
        A formatted string of upcoming events
    """

    service = get_calendar_service()
    now = datetime.now(timezone.utc).isoformat() # Fixed parentheses here

    events_results = service.events().list(
        calendarId='primary',
        timeMin=now,
        maxResults=max_results,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_results.get('items', [])
    if not events:
        return "No upcoming events found"
    
    formatted_list = []
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        formatted_list.append(f"- {event['summary']} at {start}")

    return f"I found the following events : \n"+ "\n".join(formatted_list)
@tool
def current_dateTime():
    """
    Get current date and time whenever it is required or specifically asked by the user"
    """
    return datetime.now().strftime("%A, %B %d, %Y, %I:%M %p")
@tool
def create_event(
    summary:str,
    start_datetime:str,end_datetime:str,
    location:str='',
    description:str=''):
    """
    Create a new event in the user's Google Calendar.
    
    Args:
        summary: Title/name of the event (required)
        start_datetime: Start time in ISO format (e.g., "2026-01-24T14:00:00")
        end_datetime: End time in ISO format (e.g., "2026-01-24T15:00:00")
        description: Optional description of the event
        location: Optional location of the event
    
    Returns:
        Confirmation message with event details
    """

    service=get_calendar_service()
    #build the event object
    event={
        'summary':summary,
        'location':location,
        'description':description,
        'start':{
            'dateTime':start_datetime,
            'timeZone':'Asia/Kolkata',
        },
        'end':{
            'dateTime':end_datetime,
            'timeZone':'Asia/Kolkata',
        },
    }
    #we're gonna TRY to create an EVENT
    try:
        created_event=service.events().insert(calendarId='primary',body=event).execute()
        return f"✓ Event created successfully!\n\nTitle: {summary}\nStart: {start_datetime}\nEnd: {end_datetime}\nEvent link: {created_event.get('htmlLink')}"
    except Exception as e:
        return f"❌ Failed to create event: {str(e)}"
@tool    
def update_calendar_events(
        event_summary:str,
        new_summary:str='',
        new_start_datetime:str='',
        new_end_datetime:str='',
        new_description:str='',
        new_location:str=''
)->str:
    """
    Update an existing event in the user's Google Calendar.
    First finds the event by its current title, then updates the specified fields.
    
    Args:
        event_summary: Current title of the event to find and update (required)
        new_summary: New title for the event (optional)
        new_start_datetime: New start time in ISO format (optional)
        new_end_datetime: New end time in ISO format (optional)
        new_description: New description (optional)
        new_location: New location (optional)
    
    Returns:
        Confirmation message with updated event details
    """
    service = get_calendar_service()
    try:
        now=datetime.now(timezone.utc).isoformat()
        events_results=service.events().list(
            calendarId='primary',
            timeMin=now,
            maxResults=50,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        events=events_results.get('items',[])
        search_term = event_summary.lower()
        exact_matches = []
        partial_matches = []
        target_event=None
        for event in events:
            event_title=event.get('summary','').lower()
            if event_title==search_term:
                exact_matches.append(event)
            elif search_term in event_title or event_title in search_term:
                partial_matches.append(event)
        
        matching_events=exact_matches if exact_matches else partial_matches
                
        if not matching_events:
                return f"❌ No upcoming event found with title '{event_summary}'.try listing your events to see an exact title"
        
        #if multipple matches,return them for user to clarify
        if len(matching_events)>1:
            match_list=[]
            for i,event in enumerate(matching_events[:5],1):
                start=event['start'].get('datetime',event['start'].get('date'))
                match_list.append(f"{i}. '{event.get('summary')}' on {start}")
            return f"⚠️ Found {len(matching_events)} events matching '{event_summary}':\n\n" + "\n".join(match_list) + "\n\nPlease be more specific with the event title and date/time to update the correct one."
        
        # Single match found - proceed with update
        target_event = matching_events[0]
        original_title = target_event.get('summary')         
            
            #update only feilds tht were provided

        if new_summary:
            target_event["summary"]=new_summary
        if new_start_datetime:
            target_event['start'] = {
                'dateTime': new_start_datetime,
                'timeZone': 'Asia/Kolkata'
            }
        if new_end_datetime:
            target_event['end'] = {
                'dateTime': new_end_datetime,
                'timeZone': 'Asia/Kolkata'
            }
        if new_description:
            target_event['description'] = new_description
        if new_location:
            target_event['location'] = new_location
            
        #perform update
        updated_event=service.events().update(
            calendarId='primary',
            eventId=target_event['id'],
            body=target_event
        ).execute()
        updates = []
        if new_summary:
            updates.append(f"Title: '{original_title}' → '{new_summary}'")
        if new_start_datetime:
            updates.append(f"Start: {new_start_datetime}")
        if new_end_datetime:
            updates.append(f"End: {new_end_datetime}")
        if new_location:
            updates.append(f"Location: {new_location}")
        if new_description:
            updates.append(f"Description: {new_description}")
        
        return f"✓ Event updated successfully!\n\nUpdated fields:\n" + "\n".join(updates) + f"\n\nEvent link: {updated_event.get('htmlLink')}"
            
    except Exception as e:
        return f"❌ Failed to update event: {str(e)}"
#%%
tools = [list_calendar_event,current_dateTime,create_event,update_calendar_events]


#convert tools to what groq expects
from langchain_core.utils.function_calling import convert_to_openai_tool
tool_schemas=[convert_to_openai_tool(tool) for tool in tools]
llm_with_tools = llm.bind_tools(tool_schemas)
tool_node = ToolNode(tools)

#%%what
# Add this above your assistant function

from langchain_core.messages import SystemMessage

system_prompt = SystemMessage(content="""You are a helpful calendar assistant. When you receive tool results, 
    summarize them clearly for the user. Only call tools when you need information 
    you don't have. After presenting information from tools, provide a final answer.
    
    When creating events:
    - Always get the current date/time first if the user uses relative terms like "tomorrow", "next week", etc.
    - Convert times to ISO 8601 format (YYYY-MM-DDTHH:MM:SS)
    - If the user doesn't specify end time, assume 1 hour duration
    - Ask for clarification if critical information is missing (event title, date/time)
    When updating events:
    - First list events if the user is unsure of the exact event title
    - You need the exact or partial current event title to find it
    - Only update the fields the user specifically mentions
    - Confirm what will be changed before updating
    """
)

def assistant(state: State):
    # Prepend the system prompt to the message history
    messages = [system_prompt] + state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

# 6. BUILD THE GRAPH
builder = StateGraph(State)
builder.add_node("assistant", assistant)
builder.add_node("tools", tool_node)

builder.add_edge(START, "assistant")
builder.add_conditional_edges("assistant", tools_condition)
builder.add_edge("tools", "assistant")


app = builder.compile()
#%%
#7 EXECUTION LOOP
if __name__=="__main__":
    print("---CALENDAR AGENT ACTIVE---")
    print("type 'exit','stop','quit' to stop")
    while True:
        user_input=input("user:").strip()

        #exit condition
        if user_input.lower() in (['quit','stop','exit']):
            print("Goodbye!!! 😔💔")
            break

        #package user input into graph state
        #start a new thread of conversation with this input

        inputs={"messages":[("user",user_input)]}

        #stream the graph execution

        for output in app.stream(inputs,stream_mode="updates"):
            for key,value in output.items():
                print(f"\n[Node:{key}]")

                #get last message
                last_msg=value["messages"][-1]

                #check if assistant node decided to ue tool
                if hasattr(last_msg,'tool_calls') and last_msg.tool_calls:
                    for tool_call in last_msg.tool_calls:
                        print(f"Action:calling tool '{tool_call['name']}'..")

                elif last_msg.content:
                    print(f"Assistant:{last_msg.content}")
        print("\n" + "-" * 50 + "\n")


# %%
