DEFAULT_USER_QUERY_MASK = "{USER_QUERY}"

DEFAULT_SYSTEM_PROMPT = """You are an advanced AI system specialized in understanding and parsing user query."""

DEFAULT_PARSE_USER_QUERY_PROMPT = f"""
Your task: Parse the provided user query accurately into a structured JSON format according to the attributes below. Do not introduce information not explicitly provided. If an attribute is not mentioned, use empty strings "" for strings, 0 for numbers, empty list [] for lists, and empty fields "" for dict items.

Parse Attributes:
- street_name: street_name of search place
- ward_name: ward_name of search place
- district_name: district_name of search place
- city_name: city_name of search place
- dish_names (list): one or multiple of dish names separated by comma (example dish: 'cơm gà, phở, bánh mì', 'cua', 'trà sữa', 'bánh mì chảo', 'bánh xèo', 'bún bò', 'bánh tráng trộn', 'sushi', 'ramen', 'sashimi', 'sushi cuộn', 'sashimi cuộn')
- restaurant_name (string): restaurant name, store name, place name
- avg_price (int): average price (if not mention fill ''), user can use 'k' for thousand (10k ~ 10000), 'tr' for million (1tr ~ 1000000)
- utilities (list): one or multiple utilities from the following list, separated by comma ('bán mang đi', 'ăn tại chỗ', 'giao hàng', 'đỗ xe', 'wifi', 'nhà vệ sinh', 'điều hòa').
- styles (list): one or multiple styles from the following list, separated by comma (chill out, sang trọng, giản dị, ấm áp).


Output Requirements:
- Do not include any text or commentary outside of the JSON.
- Return only the JSON, make sure the JSON is valid and properly formatted.

User query: {DEFAULT_USER_QUERY_MASK}
"""
