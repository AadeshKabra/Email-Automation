from langchain_core.tools import tool
from langchain_ollama import ChatOllama 
from browser_session import BrowserSession


browser = BrowserSession()


def get_browser():
    global _browser_instance
    if _browser_instance is None:
        _browser_instance = BrowserSession()
    
    return _browser_instance


@tool
def navigate_to_url(url):
    """Navigate to a url"""
    browser = get_browser()
    return browser.navigate(url)


@tool
def get_current_page_text():
    """Get all text from current page"""
    browser = get_browser()
    return browser.get_page_content()


@tool
def list_all_links():
    """Get all links from current page"""
    links = browser.get_all_links()
    result = f"Found {len(links)} total links. Showing first 20:\n\n"
    for i, link in enumerate(links[:20], 1):
        result += f"{i}. Text: '{link['Text']}'\n   URL: {link['Url']}\n\n"
    
    return result


@tool
def click_on_link(link_url):
    """Click on a specific link to navigate"""
    browser = get_browser()
    return browser.click_links(link_url)


@tool
def extract_information(question):
    """
    Use LLM to extract specific information from current page.
    Returns the information if found
    """
    browser = get_browser()
    content = browser.get_page_content()

    llm = ChatOllama(model="kimi-k2.5:cloud")

    prompt = f"""Based on the webpage content below, answer this question: {question}
        Webpage content:
    {content[:5000]}
    
    If you can answer the question, provide the answer.
    If the information is NOT on this page, respond with exactly: NOT FOUND
    
    Answer:
    """

    response = llm.invoke(prompt)
    return response.content


@tool
def find_link_by_text(search_text):
    """
    Find a link on the current page by searching for text.
    Useful for finding a person's name link.
    
    Example: find_link_by_text("Amol Deshpande")
    """
    browser = get_browser()
    links = browser.get_all_links()

    search_text_lower = search_text.lower()

    matches = []
    for link in links:
        if search_text_lower in link['Text'].lower():
            matches.append(link)

    if not matches:
        return "No links found"
    
    result = f"Found {len(matches)} links matching '{search_text}':\n\n"
    for i, link in enumerate(matches[:5], 1):
        result += f"{i}. Text: '{link['Text']}' Url: {link['Url']}\n"
    
    return result


@tool
def get_current_url():
    """
    Get the URL of the current page.
    
    Returns:
        The current URL or None if no page is loaded
    """
    browser = get_browser()
    url = browser.get_current_url()
    return url if url else "No page"


def close_browser():
    global _browser_instance
    if _browser_instance:
        _browser_instance.close()
        _browser_instance = None
