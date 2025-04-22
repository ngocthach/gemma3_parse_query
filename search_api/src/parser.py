import json
import logging
from configs import DEFAULT_USER_QUERY_MASK, DEFAULT_SYSTEM_PROMPT, DEFAULT_PARSE_USER_QUERY_PROMPT
from llm import chat_complete


class QueryParser:
    def __init__(self):
        self.system_prompt = DEFAULT_SYSTEM_PROMPT
        self.parse_user_query_prompt = DEFAULT_PARSE_USER_QUERY_PROMPT

    @staticmethod
    def parse_json_response(content: str) -> dict:
        """
        Post-process the JSON string to ensure it is valid and properly formatted.

        Args:
            content (str): JSON string to be post-processed.

        Returns:
            dict: Post-processed JSON object.
        """
        if content.startswith("```json"):
            content = content[7:-3].strip()
        return json.loads(content)

    async def parse_user_query(
        self, user_query: str
    ) -> dict:
        """
        Parse user query into structured JSON format.

        Args:
            user_query (str): User query string.

        Returns:
            dict: Parsed user query in structured JSON format.
        """
        prompt = self.parse_user_query_prompt.replace(DEFAULT_USER_QUERY_MASK, user_query)
        response = chat_complete(
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ],
        )
        parsed_content = self.parse_json_response(response)
        logging.info(f"Parsed user query: {parsed_content}")
        return parsed_content

query_parser = QueryParser()
