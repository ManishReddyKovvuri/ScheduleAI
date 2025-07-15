
from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.sessions import State
from google.adk.runners import Runner


from pathlib import Path
import random
import asyncio

SYSTEM_PROMPT_PATH = Path(__file__).parent.parent / "prompts/system_prompt.md"
with open(SYSTEM_PROMPT_PATH, "r") as f:
    SCHEDULER_MODEL_SYSTEM_PROMPT = f.read()

def get_current_schudule():
    """
    Returns the current schedule of the User as a string.
    """

    if random.choice([True]):
        # Simulating a schedule with a random choice
        current_schedule = [
            {"task": "Meeting with team", "time": "10:00 AM"},
            {"task": "Lunch break", "time": "12:00 PM"},
            {"task": "Project review", "time": "2:00 PM"}
        ]
        schedule_str = "\n".join([f"{item['task']} at {item['time']}" for item in current_schedule])
        return f"Current schedule:\n{schedule_str}"
    else : 
        return "Current schedule is empty."

scheduler_agent = Agent(
    name="Schedule_time_agent_v0",
    model="gemini-2.0-flash",
    description=(
        "Agent to Plan and schedule tasks based on user input."
    ),
    instruction="Plan the users day according to the user input, if timings, priorities are not mentioned, use the tools to understand current schedule in calendar and also consider the user mentioned taks as well, think of a appropriate time for that activity, include breaks for every 25mins of activity 5 mins break ",
    tools =[get_current_schudule]

)

print(f'''
Scheduler agent Name: {scheduler_agent.name}
Scheduler agent Model: {scheduler_agent.model}  
Scheduler agent Description: {scheduler_agent.description}
Scheduler agent Tools: {scheduler_agent.tools}
      ''')

# Setting up session and memory

#Session

APP_NAME ='SCHEDULER-APP'
USER_ID = 'mANISH'
SESSION_ID = 'ses_001'

session_service =InMemorySessionService()

session  = asyncio.run(session_service.create_session( app_name= APP_NAME, user_id=USER_ID, session_id= SESSION_ID))


print(f'''
Session Created      
      {session}

''')


runner = Runner(
    agent=scheduler_agent, # The agent we want to run
    app_name=APP_NAME,   # Associates runs with our app
    session_service=session_service # Uses our session manager
)
print(f"Runner created for agent '{runner.agent.name}'.")






## -----------------------------------------------------------

# @title Define Agent Interaction Function

from google.genai import types # For creating message Content/Parts

async def call_agent_async(query: str, runner, user_id, session_id):
  """Sends a query to the agent and prints the final response."""
  print(f"\n>>> User Query: {query}")

  # Prepare the user's message in ADK format
  content = types.Content(role='user', parts=[types.Part(text=query)])

  final_response_text = "Agent did not produce a final response." # Default

  # Key Concept: run_async executes the agent logic and yields Events.
  # We iterate through events to find the final answer.
  async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
      # You can uncomment the line below to see *all* events during execution
      print(f"  [Event] Author: {event.author}, Type: {type(event).__name__}, Final: {event.is_final_response()}, Content: {event.content}")

      # Key Concept: is_final_response() marks the concluding message for the turn.
      if event.is_final_response():
          if event.content and event.content.parts:
             # Assuming text response in the first part
             final_response_text = event.content.parts[0].text
          elif event.actions and event.actions.escalate: # Handle potential errors/escalations
             final_response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
          # Add more checks here if needed (e.g., specific error codes)
          break # Stop processing events once the final response is found

  print(f"<<< Agent Response: {final_response_text}")




  # We need an async function to await our interaction helper
async def run_conversation():
    await call_agent_async("Plan my task for the day  apply jobs, update resume, Have breakfast, play hockey with friends at 6Pm, wacth movie at 11 am, read novel, meal prep",
                                       runner=runner,
                                       user_id=USER_ID,
                                       session_id=SESSION_ID)

    
asyncio.run( run_conversation())