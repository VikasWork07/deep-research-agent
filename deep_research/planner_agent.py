from agents import Agent, OpenAIChatCompletionsModel
from dotenv import load_dotenv
from openai import AsyncOpenAI
from pydantic import BaseModel, Field
import os

load_dotenv(override=True)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

HOW_MANY_SEARCHES = 1
instructions = f"You are a helpful research assistant. Given a query, come up with a set of web searches \
to perform to best answer the query. Output {HOW_MANY_SEARCHES} terms to query for."

class WebSearchItem(BaseModel):
    reason: str = Field(description="Your reasoning for why this search is important to the query.")
    query: str = Field(description="The search item to use for the web search.")

class WebSearchPlan(BaseModel):
    searches: list[WebSearchItem] = Field(description="The list of web searches to perform to best answer the query.")

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
gemini_client = AsyncOpenAI(base_url=GEMINI_BASE_URL, api_key=GOOGLE_API_KEY)
gemini_model = OpenAIChatCompletionsModel(model="gemini-2.5-flash", openai_client=gemini_client)

planner_agent = Agent(
        name="Planner Agent",
        instructions=instructions,
        model=gemini_model,
        output_type=WebSearchPlan,
)

