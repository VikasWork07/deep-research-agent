from agents import Agent, OpenAIChatCompletionsModel, function_tool
from typing import Dict
import os
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv(override=True)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

@function_tool
def send_email(subject: str, html_body: str) -> dict[str, str]:
    """ Send an email with the given subject and HTML body."""
    print(f"Send email with subject: {subject}")
    print(f"Send email with body: {html_body}")
    return {"status": "success"}

instructions = """You are able to send a nicely formatted HTML email based on a detailed report.
You will be provided with a detailed report. You should use your tool to send one email, providing the 
report converted into clean, well presented HTML with an appropriate subject line."""

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
gemini_client = AsyncOpenAI(base_url=GEMINI_BASE_URL, api_key=GOOGLE_API_KEY)
gemini_model = OpenAIChatCompletionsModel(model="gemini-2.0-flash", openai_client=gemini_client)

email_agent = Agent(
    name="Email agent",
    instructions=instructions,
    tools=[send_email],
    model=gemini_model,
)