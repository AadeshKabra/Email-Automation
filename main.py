# ## **Architecture Diagram**

# User Query: "Find email of Professor Amol"
#      ↓
# [Agent Executor]
#      ↓
# [Reasoning Loop] ←──────┐
#      ↓                   │
# Can I answer? ──NO→ [Find Link] → [Click] ──┘
#      ↓                                      
#     YES                                     
#      ↓                                      
# Return Answer



from browsing_agent import create_browsing_agent
from browser_tools import browser


def main():
    agent = create_browsing_agent()

    url = "https://www.cs.umd.edu/people/phonebook/faculty"
    question = "Find the email address of Professor Amol Deshpande"

    user_input = f"""
    Starting URL: {url}
    Task: {question}
    
    Navigate to the URL first, then find the information.
    """

    result = agent.invoke({"input": user_input})

    print(result["output"])

    browser.close()



if __name__ == "__main__":
    main()

