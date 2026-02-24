from agents import Agent, ModelSettings, OpenAIChatCompletionsModel, WebSearchTool
from pydantic import BaseModel
from openai import AsyncOpenAI
import os
from dotenv import load_dotenv

load_dotenv(override=True)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

instructions =  """You are a research assistant. Given a search term, you search the web for that term and
    produce a concise summary of the results. The summary must 2-3 paragraphs and less than 300
    words. Capture the main points. Write succintly, no need to have complete sentences or good
    grammar. This will be consumed by someone synthesizing a report, so its vital you capture the
    essence and ignore any fluff. Do not include any additional commentary other than the summary itself."""

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
gemini_client = AsyncOpenAI(base_url=GEMINI_BASE_URL, api_key=GOOGLE_API_KEY)
gemini_model = OpenAIChatCompletionsModel(model="gemini-2.5-flash", openai_client=gemini_client)

search_agent = Agent(
    name="Search Agent",
    instructions=instructions,
    tools=[WebSearchTool(search_context_size="low")],
    model=gemini_model,
    model_settings=ModelSettings(tool_choice="required")
)