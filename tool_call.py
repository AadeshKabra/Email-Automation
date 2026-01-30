# import re
# import os
# from urllib.parse import urlparse
# from langchain_community.document_loaders import WebBaseLoader


# EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)

# os.environ["USER_AGENT"] = (
#     "Mozilla/5.0 (compatible; MyLangChainBot/1.0; +https://example.com/bot-info)"
# )


# def scrape_emails_from_url(url):
#     loader = WebBaseLoader(url)
#     docs = loader.load()
#     text = "\n".join(d.page_content for d in docs)

#     emails = sorted(set(EMAIL_RE.findall(text)))
#     return emails


# url = "https://www.cs.umd.edu/people/phonebook/faculty"

# emails = scrape_emails_from_url(url)
# for email in emails:
#     print(email)



# from openai import OpenAI


# client = OpenAI(
#     base_url="http://localhost:11434/v1",
#     api_key="ollama" #dummy value
# )

# resp = client.chat.completions.create(
#     model="llama3.2",
#     messages=[
#         {"role": "system", "content": "You are a helpful web scraping agent"},
#         {"role": "user", "content": "Extract all emails from this link: 'https://me.umd.edu/clark/facultydir?facultylayout=0'. This link is a public link of all faculties in CS department of UMD-College park."}
#     ],
#     temperature=0.2,
# )

# print(resp.choices[0].message.content)







# Sample Tool call

# from langchain_ollama import ChatOllama
# from langchain_core.tools import tool
# from langgraph.prebuilt import create_react_agent
# from langgraph.checkpoint.memory import MemorySaver

# @tool
# def multiply(x: float, y: float) -> float:
#     """Multiply x times y."""
#     return x * y

# llm = ChatOllama(model="llama3.2", temperature=0)
# tools = [multiply]

# # LangGraph's create_react_agent replaces the old pattern
# agent = create_react_agent(llm, tools)

# # Use InMemorySaver for conversation memory (optional)
# memory = MemorySaver()
# agent = agent.with_config({"configurable": {"thread_id": "1"}})

# # Invoke directly (no AgentExecutor needed)
# result = agent.invoke({"messages": [("human", "Compute 6 * 7 using the tool, then explain.")]})
# print(result["messages"][-1].content)



import os
import re
from typing import List
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
# from langgraph.prebuilt import create_react_agent
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_community.document_loaders import WebBaseLoader
from bs4 import BeautifulSoup


os.environ["USER_AGENT"] = "Mozilla/5.0 (compatible; UMDCSTool/1.0)"

@tool
def scrape_emails(link:str) -> str:
    """Scrape all email addresses from a webpage. 
    Use this when the user asks to extract emails from a specific URL.
    
    Args:
        link: The webpage URL to scrape (must be publicly accessible)
    
    Returns:
        Formatted list of all unique emails found on the page.
    """
    loader = WebBaseLoader(link)
    docs = loader.load()
    html = docs[0].page_content

    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text()

    EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)

    emails = re.findall(EMAIL_RE, text)

    dot_pattern = r'([A-Za-z0-9._%+-]+)\[?\.?\[dot\]?([A-Za-z0-9.-]+)\[?\.?\[dot\]?([a-z]{2,})'
    dot_matches = re.findall(dot_pattern, text, re.I)

    for match in dot_matches:
        email = f"{match[0]}@{match[1]}.{match[2]}".lower()
        if email not in emails:
            emails.append(email)

    emails = sorted(list(set([e.lower() for e in emails])))

    return f"Found {len(emails)} emails:\n" + "\n".join(emails)


llm = ChatOllama(model="kimi-k2.5:cloud", temperature=0)
tools = [scrape_emails]

# agent = create_react_agent(llm, tools)
agent = create_agent(llm, tools)
memory = MemorySaver()

agent = agent.with_config({"configurable": {"thread_id": 1}})

result = agent.invoke({"messages": [("human", "Scrape the website 'https://www.rhsmith.umd.edu/directory' and get me the email-ids of all the professors listed on the page. Go to the all pages on the website and fetch complete list of the email-ids")]})

print(result["messages"][-1].content)