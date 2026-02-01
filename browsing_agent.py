from langgraph.prebuilt import create_react_agent
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from browser_tools import (navigate_to_url, get_current_page_text, list_all_links, click_on_link, extract_information, find_link_by_text)


def create_browsing_agent():
    """Create an agent that can browse websites"""

    tools = [
        navigate_to_url, get_current_page_text, list_all_links, click_on_link, extract_information, find_link_by_text
    ]

    llm = ChatOllama(model="kimi-k2.5:cloud", temperature=0)

    prompt = """
        You are a web browsing agent that can navigate websites to find information.

    Your strategy:
    1. First, use get_current_page_text to see what's on the current page
    2. Use extract_information to check if the answer is on this page
    3. If answer is NOT FOUND:
    - Use list_all_links to see available links
    - Find the most relevant link (e.g., person's name)
    - Use click_on_link to navigate there
    - Repeat from step 1
    4. Once you find the answer, return it

    Example task: "Find email of Professor John Doe"
    - Step 1: Check current page for email → NOT FOUND
    - Step 2: List links → Find "John Doe" link
    - Step 3: Click on John Doe's profile
    - Step 4: Extract email → Found!

    Be systematic and don't give up easily.
    Question: {input}
    """

    # prompt = ChatPromptTemplate.from_messages([("system", """You are a web browsing agent that can navigate websites to find information.

    # Your strategy:
    # 1. First, use get_current_page_text to see what's on the current page
    # 2. Use extract_information to check if the answer is on this page
    # 3. If answer is NOT FOUND:
    # - Use list_all_links to see available links
    # - Find the most relevant link (e.g., person's name)
    # - Use click_on_link to navigate there
    # - Repeat from step 1
    # 4. Once you find the answer, return it

    # Example task: "Find email of Professor John Doe"
    # - Step 1: Check current page for email → NOT FOUND
    # - Step 2: List links → Find "John Doe" link
    # - Step 3: Click on John Doe's profile
    # - Step 4: Extract email → Found!

    # Be systematic and don't give up easily."""), 
    # ("human", "{input}"), ("placeholder", "{agent_scratchpad}")])
    

    agent = create_react_agent(llm, tools)

    # executor = AgentExecutor(agent, tools, verbose=True, max_iterations=15, handle_parsing_errors=True)

    return agent


