from agents import Agent, OpenAIChatCompletionsModel
from pydantic import BaseModel, Field
from openai import AsyncOpenAI
import os
from dotenv import load_dotenv

load_dotenv(override=True)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
gemini_client = AsyncOpenAI(base_url=GEMINI_BASE_URL, api_key=GOOGLE_API_KEY)
gemini_model = OpenAIChatCompletionsModel(model="gemini-2.5-flash", openai_client=gemini_client)

class ClarifierOutput(BaseModel):
    needs_clarification: bool = Field(description="Whether the research query needs clarification.")
    clarifying_questions: list[str] | None = Field(description="List of clarifying questions if needs_clarification is True.")

instructions = """ You are a research scope validator.

If the user's research query is:
- Too broad
- Missing domain constraints
- Missing geography
- Missing timeframe
- Missing depth specification

Then set needs_clarification = true and provide 2-5 concise clarifying questions.

If the request is sufficiently specific for deep research,
set needs_clarification = false.
"""

clarifier_agent = Agent(
    name="Clarifier Agent",
    instructions=instructions,
    model=gemini_model,
    output_type=ClarifierOutput
)