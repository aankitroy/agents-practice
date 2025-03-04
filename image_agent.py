# from agno.agent import Agent
# from agno.media import Image
# from agno.models.openai import OpenAIChat
# from agno.tools.duckduckgo import DuckDuckGoTools

# agent = Agent(
#     model=OpenAIChat(id="gpt-4o"),
#     tools=[DuckDuckGoTools()],
#     markdown=True,
# )

# agent.print_response(
#     "Tell me about this image and give me the latest news about it.",
#     images=[
#         Image(
#             url="https://upload.wikimedia.org/wikipedia/commons/0/0c/GoldenGateBridge-001.jpg"
#         )
#     ],
#     stream=True,
# )


from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.dalle import DalleTools

image_agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    tools=[DalleTools()],
    description="You are an AI agent that can generate images using DALL-E.",
    instructions="When the user asks you to create an image, use the `create_image` tool to create the image.",
    markdown=True,
    show_tool_calls=True,
)

image_agent.print_response("Generate an image of a white siamese cat")

images = image_agent.get_images()
if images and isinstance(images, list):
    for image_response in images:
        image_url = image_response.url
        print(image_url)