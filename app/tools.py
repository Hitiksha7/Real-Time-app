import os
from dotenv import load_dotenv
from langchain_tavily import TavilySearch

load_dotenv()

search_tool = TavilySearch(
    api_key=os.getenv("TAVILY_API_KEY"),  # Changed from tavily_api_key
    max_results=5
)


def tavily_search(query: str):
    """Search the web for current information using Tavily search engine."""
    return search_tool.invoke(query)


tools = [tavily_search]