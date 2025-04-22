import logging
import os

import requests
from function_schema import get_function_schema

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


SEARCH_API_HOST = os.getenv("SEARCH_API_HOST", "localhost")
SEARCH_API_PORT = os.getenv("SEARCH_API_PORT", "8085")

def search_restaurant(query):
    """
    Search for restaurants based on user query

    Parameters:
        query (str): User query

    Returns:
        list[dict]: List of restaurants
    """
    url = f"http://{SEARCH_API_HOST}:{SEARCH_API_PORT}/v1/llm-search"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    payload = {"query": query}

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        logger.info("Response from search API: %s", response.json())
        return response.json()['data']
    except requests.RequestException as e:
        logging.error(f"Error while searching for restaurants: {e}")
        return []


def search_restaurant_with_details(
        restaurant_name=None,
        dish_name=None,
        avg_price=None,
        utility=None,
        styles=None,
        ward_name=None,
        district_name=None,
        city_name=None
):
    """
    Search for restaurants based on user query and additional filters.

    Parameters:
        restaurant_name (str, optional): Name of the store
        dish_name (str, optional): Name of the dish
        avg_price (int, optional): Average price of the dish
        utility (list[str], optional): List of utilities
        styles (list[str], optional): List of styles descriptions
        ward_name (str, optional): Ward name
        district_name (str, optional): District name
        city_name (str, optional): City name

    Returns:
        list[dict]: List of restaurants
    """
    url = f"http://{SEARCH_API_HOST}:{SEARCH_API_PORT}/v1/search"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    payload = {
        "restaurant_name": restaurant_name,
        "dish_name": dish_name,
        "avg_price": avg_price,
        "utility": utility,
        "styles": styles,
        "ward_name": ward_name,
        "district_name": district_name,
        "city_name": city_name
    }

    # Remove keys with None values
    payload = {key: value for key, value in payload.items() if value is not None}

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()['data']
    except requests.RequestException as e:
        logging.error(f"Error while searching for restaurants: {e}")
        return []

def get_tool_schema(function):
    return {
        "type": "function",
        "function": get_function_schema(function)
    }
