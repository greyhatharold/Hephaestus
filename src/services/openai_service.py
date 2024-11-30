from openai import OpenAI
from typing import Any
from utils.logger import get_logger

logger = get_logger(__name__)

class OpenAIService:
    def __init__(self):
        self.client = OpenAI()
    
    def create_completion(self, prompt: str, model: str = "gpt-4") -> str:
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise 