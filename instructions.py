from agno.agent import Agent

from dotenv import load_dotenv

load_dotenv()

agent = Agent(
    description="You are a famous short story writer asked to write for a magazine",
    instructions=["You are a pilot on a plane flying from Hawaii to Japan."],
    markdown=True,
    debug_mode=True,
)
agent.print_response("Tell me a 2 sentence horror story.", stream=True)