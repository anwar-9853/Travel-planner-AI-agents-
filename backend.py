import os 
import requests
import certifi
import uuid
import operator 
from typing import Annotated, TypedDict
from dotenv import load_dotenv
from psycopg_pool import ConnectionPool  
from langchain_openrouter import ChatOpenRouter
from langchain_openai import ChatOpenAI

import psycopg 
from psycopg.rows import dict_row
from langgraph.graph import StateGraph, START, END 
from langgraph.checkpoint.postgres import PostgresSaver
from langchain_core.messages import (
    AnyMessage, 
    HumanMessage,
    SystemMessage,
    AIMessage
)
load_dotenv()
os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUEST_CA_BUNDLE"] = certifi.where()

def search_flights(query: str) -> str:
    return f"Flight availability for {query}"

def tavily_search(query: str) -> str:
    return f"Hotel details from web search for {query}"

llm = ChatOpenAI(
    model="openrouter/free",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)


def get_database_url():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL is missing.")
    if "sslmode" not in database_url:
        separator = "&" if "?" in database_url else "?"
        database_url = f"{database_url}{separator}sslmode=require"
    return database_url

class Travelstate():
    messages: Annotated[list[AnyMessage], operator.add]
    user_query: str
    flight_results: str
    hotel_results: str
    itinerary: str  # Kept as 'itinerary' to match downstream keys
    llm_calls: int

# FLIGHT AGENT 
def flight_agent(state: Travelstate):
    query = state["user_query"]
    flight_data = search_flights(query)
    return {
        "flight_results": flight_data,
        "messages":[
            AIMessage(content="Flight results fetched.")
        ],
        "llm_calls": state.get("llm_calls", 0) + 1
    }


# HOTEL AGENT
def hotel_agent(state: Travelstate):
    query = f"Best hotels for {state['user_query']}"
    hotel_results = tavily_search(query)
    return {
        "hotel_results": hotel_results, # Fixed typo from "hotel_resutls"
        "messages": [
            AIMessage(content="Hotel information fetched.") # Fixed typo from "AIMessages"
        ],
        "llm_calls": state.get("llm_calls", 0) + 1
    }
 
def itinerary_agent(state: Travelstate): 
    prompt = f"""Create a complete travel itinerary.
User Query:
    {state['user_query']}
Flight Results:
    {state['flight_results']}
Hotel Results:
    {state['hotel_results']}

Make the itinerary practical, budget-aware, and easy to follow""" 

    response = llm.invoke([
        SystemMessage(content="You are an expert travel planner."),
        HumanMessage(content=prompt)
    ])
    return {
        "itinerary": response.content,
        "messages": [response], 
        "llm_calls": state.get("llm_calls", 0) + 1
    }

def final_agent(state: Travelstate):
    final_prompt = f"""
Generate the final travel response for the user 
User Request:
{state['user_query']}
Flights:
{state['flight_results']}
Hotels:
{state['hotel_results']}
Itinerary:
{state['itinerary']}

Format the final answer beautifully using these sections:
1. Trip Summary
2. Flight Information
3. Hotel Suggestions
4. Day by Day Itinerary
5. Estimated Budget
6. Final Recommendations

Important:
- Be clear and practical 
- Mention the live flight API may not provide ticket price if the pricing is unavailable
- Keep the response useful for real travel planning.
"""
    response = llm.invoke([
        SystemMessage(content="You are a professional AI travel booking assistant."),
        HumanMessage(content=final_prompt)
    ])
    return {
        "messages": [response], 
        "llm_calls": state.get("llm_calls", 0) + 1
    }


# BUILD THE GRAPH
graph = StateGraph(Travelstate)
graph.add_node("flight_agent", flight_agent)
graph.add_node("hotel_agent", hotel_agent)
graph.add_node("itinerary_agent", itinerary_agent)
graph.add_node("final_agent", final_agent)

# EDGE CONNECTIONS
graph.add_edge(START, "flight_agent")
graph.add_edge("flight_agent", "hotel_agent")
graph.add_edge("hotel_agent", "itinerary_agent")
graph.add_edge("itinerary_agent", "final_agent")
graph.add_edge("final_agent", END)
#  POSTGRESQL CHECKPOINTER 
DATABASE_URL = get_database_url()

# Create a persistent connection pool context manager
checkpointer_context = PostgresSaver.from_conn_string(DATABASE_URL)

# Enter the context manager to extract the actual checkpointer object
checkpointer = checkpointer_context.__enter__()

# Setup tables if they don't exist
checkpointer.setup()

# Compile the graph using the live checkpointer
travel_graph = graph.compile(checkpointer=checkpointer)


# FASTAPI BACKEND FUNCTION
def run_travel_agent(user_input: str, thread_id: str | None = None):
    if not thread_id:
        thread_id = f"user_{uuid.uuid4().hex}"
    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }
    
    # Using the context compiled graph safely
    result = travel_graph.invoke(
        {
            "messages": [
                HumanMessage(content=user_input)
            ],
            "user_query": user_input, 
            "flight_results": "", 
            "hotel_results": "", 
            "itinerary": "",
            "llm_calls": 0
        },
        config=config
    )
    
    final_answer = result['messages'][-1].content
    return {
        "thread_id": thread_id,
        "answer": final_answer,
        "flight_results": result.get("flight_results", ""), 
        "hotel_results": result.get("hotel_results", ""),   
        "itinerary": result.get("itinerary", ""),
        "llm_calls": result.get("llm_calls", 0)
    }
