import asyncio

import nest_asyncio
import streamlit as st
from agno.tools.streamlit.components import check_password

from css import CUSTOM_CSS
from utils import about_agno, footer
nest_asyncio.apply()

st.set_page_config(
    page_title="Agno Agents",
    page_icon=":orange_heart:",
    layout="wide",
)
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


async def header():
    st.markdown("<h1 class='heading'>Agno Agents</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p class='subheading'>Welcome to the Agno Agents platform! We've provided some sample agents to get you started.</p>",
        unsafe_allow_html=True,
    )


async def body():
    st.markdown("### Available Agents")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            """
        <div style="padding: 20px; border-radius: 10px; border: 1px solid #ddd; margin-bottom: 20px;">
            <h3>Knowledge Agent</h3>
            <p>A knowledge agent that uses Agentic RAG to deliver context-rich answers from a knowledge base.</p>
            <p>Perfect for exploring your own knowledge base.</p>
        </div>
        """,
            unsafe_allow_html=True,
        )
        if st.button("Launch Knowledge Agent", key="knowledge_agent_button"):
            st.switch_page("pages/Knowledge.py")
    with col2:
        st.markdown(
            """
        <div style="padding: 20px; border-radius: 10px; border: 1px solid #ddd; margin-bottom: 20px;">
            <h3>Query Decomposition Agent</h3>
            <p>A query decomposition agent that decomposes a high-level analytical question into a series of sub-questions.</p>
            <p>Perfect for exploring your own knowledge base.</p>
        </div>
        """,
            unsafe_allow_html=True,
        )   
        if st.button("Launch Query Decomposition Agent", key="query_decomposition_agent_button"):
            st.switch_page("pages/QueryDecomposition.py")
    with col3:
        st.markdown(
            """
        <div style="padding: 20px; border-radius: 10px; border: 1px solid #ddd; margin-bottom: 20px;">
            <h3>Funnel Analysis Planning Agent</h3>
            <p>A funnel analysis planning agent that decomposes a high-level funnel analysis question into a series of sub-questions.</p>
            <p>Perfect for exploring your own funnel analysis questions.</p>
        </div>
        """,
            unsafe_allow_html=True,
        )       
        if st.button("Launch Funnel Analysis Planning Agent", key="funnel_analysis_planning_agent_button"):
            st.switch_page("pages/FunnelAnalysisPlanning.py")

async def main():
    await header()
    await body()
    await footer()
    await about_agno()


if __name__ == "__main__":
    if check_password():
        asyncio.run(main())
