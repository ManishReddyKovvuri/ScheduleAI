import datetime
from zoneinfo import ZoneInfo
from google.adk.agents import Agent
from pathlib import Path


SYSTEM_PROMPT_PATH = Path(__file__).parent.parent / "prompts/system_prompt.md"
with open(SYSTEM_PROMPT_PATH, "r") as f:
    REASONING_MODEL_SYSTEM_PROMPT = f.read()
root_agent = Agent(
    name="weather_time_agent",
    model="gemini-2.0-flash",
    description=(
        "Agent to answer questions about the time and weather in a city."
    ),
    instruction=REASONING_MODEL_SYSTEM_PROMPT
)

