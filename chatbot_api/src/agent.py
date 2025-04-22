import logging

from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI
from llama_index.core.tools import BaseTool, FunctionTool
from functions import search_restaurant

def multiply(a: int, b: int) -> int:
    """Multiply two integers and returns the result integer"""
    return a * b


def add(a: int, b: int) -> int:
    """Add two integers and returns the result integer"""
    return a + b

def subtract(a: int, b: int) -> int:
    """Subtract two integers and returns the result integer"""
    return a - b


def divide(a: int, b: int) -> float:
    """Divide two integers and returns the result float"""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b


search_restaurant_tool = FunctionTool.from_defaults(fn=search_restaurant)

llm = OpenAI(model="gpt-4o-mini")
ai_agent = ReActAgent.from_tools(
    tools=[
        search_restaurant_tool,
    ],
    llm=llm,
    verbose=True
)

def get_agent_response(question):
    response = ai_agent.chat(question)
    logging.info(f"Agent response: {response}")
    return response.response
