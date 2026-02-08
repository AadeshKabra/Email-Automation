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

    url = "https://www.cs.umd.edu/people/faculty"
    # url = "https://me.umd.edu/clark/facultydir?facultylayout=1"
    # question = "Find me the names of professors whose research interest is in Natural Language Processing"
    # question = "Give me email-ids of all professors having research interest in Natural Language Processing"
    # question = "Find email of Professor Jordan Boyd-Graber"
    # question = "What is professor Hanan Samet's research domain?"
    # question = "What is professor Mohit's personal website?"
    # question = "I want to know about professor Aravind Srinivasan's research interests and email id. Find the information for me."
    # question = "Who are the professors working in the area of Computer Vision? First find their names and then sequentially give their email-ids."
    # question = "I want to know about professor David Van Horn. Please give me complete information including his research interests and email id and his personal website link"
    question = "Give me the email-ids of following professors: Aravind Srinivasan, David Van Horn, Hanan Samet, Jordan Boyd-Graber. "


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

