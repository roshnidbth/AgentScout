from dotenv import load_dotenv
load_dotenv()
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from tenacity import retry, stop_after_attempt, wait_exponential
import os
from loguru import logger

class ProductionLLM:
    def __init__(self):
        self.groq = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.1,
            api_key=os.getenv("GROQ_API_KEY"),
            max_tokens=2048,
        )
        self.gemini = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.1,
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            max_output_tokens=2048,
        )
        self.primary = self.groq

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=8))
    def invoke(self, messages, **kwargs):
        try:
            return self.primary.invoke(messages, **kwargs)
        except Exception as e:
            logger.warning(f"Primary failed: {e}. Switching to fallback...")
            self.primary = self.gemini
            return self.primary.invoke(messages, **kwargs)

llm = ProductionLLM()