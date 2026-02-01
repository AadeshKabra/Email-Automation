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
from browser_tools import close_browser


def main():
    agent = create_browsing_agent()

    # url = "https://www.cs.umd.edu/people/faculty"
    url = "https://me.umd.edu/clark/facultydir?facultylayout=1"
    question = "Find the email address of Amr Baz"
    # question = "Give me email-ids of all professors having research interest in Natural Language Processing"

    user_input = f"""
    Starting URL: {url}
    Task: {question}
    
    Navigate to the URL first, then find the information.
    """

    result = agent.invoke({"input": user_input})

    print(result["output"])

    close_browser()



if __name__ == "__main__":
    main()

