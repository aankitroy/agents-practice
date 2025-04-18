import asyncio

import nest_asyncio
import streamlit as st
from agno.agent import Agent
from agno.tools.streamlit.components import check_password
from agno.utils.log import logger

from funnel_analysis_planning import get_funnel_analysis_planning_agent

from ui.css import CUSTOM_CSS
from ui.utils import (
    about_agno,
    add_message,
    display_tool_calls,
    example_inputs,
    initialize_agent_session_state,
    selected_model,
    session_selector,
    utilities_widget,
)

nest_asyncio.apply()

st.set_page_config(
    page_title="Funnel Analysis Planning",
    page_icon=":crystal_ball:",
    layout="wide",
)
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
agent_name = "funnel_analysis_planning"

async def header():
    st.markdown("<h1 class='heading'>Funnel Analysis Planning</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p class='subheading'>A funnel analysis planning agent that uses DuckDuckGo to deliver in-depth answers about any topic.</p>",
        unsafe_allow_html=True,
    )


async def body() -> None:
    ####################################################################
    # Initialize User and Session State
    ####################################################################
    user_id = st.sidebar.text_input(":technologist: Username", value="Ava")

    ####################################################################
    # Model selector
    ####################################################################
    model_id = await selected_model()

    ####################################################################
    # Initialize Agent
    ####################################################################
    funnel_analysis_planning: Agent
    if (
        agent_name not in st.session_state
        or st.session_state[agent_name]["agent"] is None
        or st.session_state.get("selected_model") != model_id
    ):
        logger.info("---*--- Creating Funnel Analysis Planning agent ---*---")
        funnel_analysis_planning = get_funnel_analysis_planning_agent(user_id=user_id, model_id=model_id)
        st.session_state[agent_name]["agent"] = funnel_analysis_planning
        st.session_state["selected_model"] = model_id
    else:
        funnel_analysis_planning = st.session_state[agent_name]["agent"]

    ####################################################################
    # Load Agent Session from the database
    ####################################################################
    try:
        st.session_state[agent_name]["session_id"] = funnel_analysis_planning.load_session()
    except Exception:
        st.warning("Could not create Funnel Analysis Planning session, is the database running?")
        return

    ####################################################################
    # Load agent runs (i.e. chat history) from memory is messages is empty
    ####################################################################
    if funnel_analysis_planning.memory:
        agent_runs = funnel_analysis_planning.memory.runs
        if len(agent_runs) > 0:
            # If there are runs, load the messages
            logger.debug("Loading run history")
            # Clear existing messages
            st.session_state[agent_name]["messages"] = []
            # Loop through the runs and add the messages to the messages list
            for agent_run in agent_runs:
                if agent_run.message is not None:
                    await add_message(agent_name, agent_run.message.role, str(agent_run.message.content))
                if agent_run.response is not None:
                    await add_message(
                        agent_name, "assistant", str(agent_run.response.content), agent_run.response.tools
                    )

    ####################################################################
    # Get user input
    ####################################################################
    if prompt := st.chat_input("✨ What would you like to know, bestie?"):
        await add_message(agent_name, "user", prompt)

    ####################################################################
    # Show example inputs
    ####################################################################
    await example_inputs(agent_name)

    ####################################################################
    # Display agent messages
    ####################################################################
    for message in st.session_state[agent_name]["messages"]:
        if message["role"] in ["user", "assistant"]:
            _content = message["content"]
            if _content is not None:
                with st.chat_message(message["role"]):
                    # Display tool calls if they exist in the message
                    if "tool_calls" in message and message["tool_calls"]:
                        display_tool_calls(st.empty(), message["tool_calls"])
                    st.markdown(_content)

    ####################################################################
    # Generate response for user message
    ####################################################################
    last_message = st.session_state[agent_name]["messages"][-1] if st.session_state[agent_name]["messages"] else None
    if last_message and last_message.get("role") == "user":
        user_message = last_message["content"]
        logger.info(f"Responding to message: {user_message}")
        with st.chat_message("assistant"):
            # Create container for tool calls
            tool_calls_container = st.empty()
            resp_container = st.empty()
            with st.spinner(":thinking_face: Thinking..."):
                response = ""
                try:
                    # Run the agent and stream the response
                    run_response = await funnel_analysis_planning.arun(user_message, stream=True)
                    async for resp_chunk in run_response:
                        # Display tool calls if available
                        if resp_chunk.tools and len(resp_chunk.tools) > 0:
                            display_tool_calls(tool_calls_container, resp_chunk.tools)

                        # Display response
                        if resp_chunk.content is not None:
                            response += resp_chunk.content
                            resp_container.markdown(response)

                    # Add the response to the messages
                    if funnel_analysis_planning.run_response is not None:
                        await add_message(agent_name, "assistant", response, funnel_analysis_planning.run_response.tools)
                    else:
                        await add_message(agent_name, "assistant", response)
                except Exception as e:
                    logger.error(f"Error during agent run: {str(e)}", exc_info=True)
                    error_message = f"Sorry, I encountered an error: {str(e)}"
                    await add_message(agent_name, "assistant", error_message)
                    st.error(error_message)

    ####################################################################
    # Session selector
    ####################################################################
    await session_selector(agent_name, funnel_analysis_planning, get_funnel_analysis_planning_agent, user_id, model_id)

    ####################################################################
    # About section
    ####################################################################
    await utilities_widget(agent_name, funnel_analysis_planning)

async def main():
    await initialize_agent_session_state(agent_name)
    await header()
    await body()
    await about_agno()


if __name__ == "__main__":
    if check_password():
        asyncio.run(main())
