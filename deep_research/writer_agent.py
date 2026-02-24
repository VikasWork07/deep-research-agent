import os
from agents import Agent, OpenAIChatCompletionsModel
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv(override=True)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

instructions=""" You are a senior researcher tasked with writing a cohesive report for a research query.
    You will be provided with the original query, and some initial research done by a research assistant.\n
    You should first come up with an outline for the report that describes the structure and
    flow of the report. Then, generate the report and return that as your final output.\n
    The final output should be in markdown format, and it should be lengthy and detailed. Aim
    for 5-10 pages of content, at least 1000 words."""

class ReportData(BaseModel):
    short_summary: str = Field(description="")
    markdown_report: str = Field(description="")
    follow_up_questions: list[str] = Field(description="")

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
gemini_client = AsyncOpenAI(base_url=GEMINI_BASE_URL, api_key=GOOGLE_API_KEY)
gemini_model = OpenAIChatCompletionsModel(model="gemini-2.5-flash", openai_client=gemini_client)

writer_agent = Agent(
    name="WriterAgent",
    instructions=instructions,
    model=gemini_model,
    output_type=ReportData,
)