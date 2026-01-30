# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.support.ui import WebDriverWait
# from webdriver_manager.chrome import ChromeDriverManager
# from bs4 import BeautifulSoup
# import re
# import time
# from typing import List
# from langchain_core.tools import tool


# @tool
# def scrape_faculty(link):
#     """
#     Navigate to faculty directory, click ALL `/people/username` profile links,
#     visit each profile page, and extract email addresses.
    
#     Args:
#         link: Main faculty directory page (e.g., "https://example.com/faculty")
    
#     Returns:
#         Complete list of all faculty emails found across all profile pages.
#     """
#     options = Options()
#     options.add_argument("--headless")
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-dev-shm-usage")
#     driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


#     all_emails = set()  

#     try:
#         driver.get(link)
#         time.sleep(3)

#         profile_links = driver.find_elements()

#         wait = WebDriverWait(driver, 15)

#         faculty_links = wait.until(
#             EC.presence_of_all_elements_located(
#                 (By.CSS_SELECTOR, 'a[href^="/people/"]')
#             )
#         )

#         print("Faculty Links: ", faculty_links)

#         for i, link_element in enumerate(faculty_links):
#             try:
#                 href = link_element.get_attribute('href')
#                 complete_url = href if href.startswith('http') else link.rstrip("/") + href
#                 faculty_name = link_element.text.strip()

#                 driver.execute_script("arguments[0].scrollIntoView();", link_element)
#                 link_element.click()

#                 wait.until(lambda d: d.current_url != link)
#                 time.sleep(2)

#                 page_source = driver.page_source
#                 soup = BeautifulSoup(page_source, 'html.parser')
#                 text = soup.get_text()

#                 EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
#                 emails = EMAIL_RE.findall(text)

#                 dot_pattern = r'([A-Za-z0-9._%+-]+)\[?\.?\[dot\]?([A-Za-z0-9.-]+)\[?\.?\[dot\]?([a-z]{2,})'
#                 for match in re.findall(dot_pattern, text, re.I):
#                     emails.append(f"{match[0]}@{match[1]}.{match[2]}")


#                 new_emails = {e.lower() for e in emails if '@' in e and len(e) > 5}
#                 all_emails.update(new_emails)
#             except Exception as e:
#                 print(e)
#     finally:
#         driver.quit()

#     result = f"""
#         Emails: {all_emails}
#     """
#     return result


# # @tool
# # def scrape_pages():



# from langchain_ollama import ChatOllama
# from langchain.agents import create_agent
# from langchain_core.messages import HumanMessage


# llm = ChatOllama(model="llama3.2", temperature=0)
# tools = [scrape_faculty]

# agent = create_agent(llm, tools)

# result = agent.invoke({
#     "messages": [HumanMessage(content="Go to the faculty directory at https://www.cs.umd.edu/people/phonebook/faculty and extract ALL professor emails by clicking each /people/ profile link")]
# })

# print(result["messages"][-1].content)







import os
import re
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


class IntelligentWebScraper():
    """
    An intelligent web scraper that uses LLM to extract information from webpages
    based on natural language queries.
    """

    def __init__(self, model_name="kimi-k2.5:cloud", base_url=None):
        self.llm = ChatOllama(model=model_name, base_url=base_url, temperature=0.5)
        self.driver = None

    
    def init_driver(self):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")

        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )

        self.driver.implicitly_wait(10)

    
    def scrape_page(self, url):
        """
        Scrape a webpage and extract clean text content.
        
        Args:
            url: URL to scrape
            
        Returns:
            Dictionary with 'text', 'html', and 'url'
        """
        self.init_driver()
        self.driver.get(url)

        WebDriverWait(self.driver, 15).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

        soup = BeautifulSoup(self.driver.page_source, 'html.parser')

        for element in soup(['script', 'style', 'nav', 'footer', 'header']):
            element.decompose()

        text = soup.get_text(separator="\n", strip=True)

        lines = [line.strip() for line in text.splitlines() if line.strip()]
        clean_text = '\n'.join(lines)
        
        return {
            'text': clean_text,
            'html': str(soup),
            'url': url
        }
    

    def query(self, url, question, output_format="text"):
        """
        Scrape a webpage and answer a question about its content using LLM.
        
        Args:
            url: URL to scrape
            question: Natural language question to answer
            output_format: "text" for natural language, "json" for structured data
            
        Returns:
            Answer to the question based on webpage content
        """
        page_data = self.scrape_page(url)

        text = page_data['text']

        if output_format == "json":
            system_message = """You are a precise data extraction assistant. 
            Extract information from the webpage content and return ONLY valid JSON.
            Format your response as a JSON object or array as appropriate for the question.
            Do not include any explanatory text, only the JSON."""

            prompt = ChatPromptTemplate.from_messages([
                ('system', system_message),
                ("human", """Webpage URL: {url}

                Webpage Content:
                {content}

                Question: {question}

                Respond with ONLY valid JSON, no other text.""")
            ])

        else:
            system_message = """You are a helpful assistant that extracts specific information from webpages.
            Answer questions accurately based ONLY on the webpage content provided.
            If the information is not found, say so clearly.
            Be concise but complete in your answers."""

            prompt = ChatPromptTemplate.from_messages([
                ("system", system_message),
                ("human", """Webpage URL: {url}

                Webpage Content:
                {content}

                Question: {question}

                Answer:""")
            ])

        chain = prompt | self.llm | StrOutputParser()

        answer = chain.invoke({
            "url": url,
            "content": text,
            "question": question
        })

        return answer.strip()
    

    def extract_structured_data(self, url, schema):
        """
        Extract structured data from a webpage according to a schema.
        
        Args:
            url: URL to scrape
            schema: Dictionary describing what to extract
                    Example: {
                        "professors": [
                            {"name": "string", "research_area": "string", "email": "string"}
                        ]
                    }
        
        Returns:
            Extracted data matching the schema
        """

        question = f"""Extract all data matching this schema: {json.dumps(schema, indent=2)}"""

        result = self.query(url, question, output_format="json")

        try:
            return json.loads(result)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            json_match = re.search(r'```(?:json)?\s*(\{.*?\}|\[.*?\])\s*```', result, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            else:
                print("Could not parse JSON response")
                return {"raw_response": result}
            

    def close(self):
        if self.driver:
            self.driver.quit()
            self.driver = None

    
    def __enter__(self):
        return self
    

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()




with IntelligentWebScraper() as scraper:
    # url = "https://www.cs.umd.edu/people/faculty"
    url = "https://www.cs.umd.edu/people/amol"

    questions = [
            "Can you give me email-id of the professor in the link?"
        ]
    
    for question in questions:
        print(f"\n {question}")
        answer = scraper.query(url, question)
        print(f" {answer}\n")
        print("-" * 70)



# import os
# import re
# import time
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
# from webdriver_manager.chrome import ChromeDriverManager
# from bs4 import BeautifulSoup
# from langchain_core.tools import tool
# from langchain_ollama import ChatOllama
# from langchain.agents import create_agent
# from langchain_core.messages import HumanMessage

# @tool
# def scrape_faculty_profiles(base_url: str) -> str:
#     """Extracts ALL faculty emails by clicking /people/ profile links."""
    
#     options = Options()
#     options.add_argument("--headless")
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-dev-shm-usage")
#     options.add_argument("--disable-gpu")
    
#     driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
#     driver.implicitly_wait(10)
    
#     all_emails = set()
    
#     def find_faculty_links() -> list:
#         """STALE-PROOF: Always re-find links fresh each iteration."""
#         return driver.find_elements(By.CSS_SELECTOR, 'a[href^="/people/"]')
    
#     try:
#         print("Loading faculty directory...")
#         driver.get(base_url)
#         time.sleep(5)
        
#         wait = WebDriverWait(driver, 15)
        
#         # MAIN LOOP: REFRESH LINKS EVERY TIME (STALE-PROOF)
#         max_profiles = 20  # Test first
#         processed = 0
        
#         while processed < max_profiles:
#             # REFRESH LINK LIST EVERY ITERATION
#             links = find_faculty_links()
#             if not links:
#                 print("No /people/ links found - trying alternative selectors...")
#                 # Try table links from your attachment
#                 links = driver.find_elements(By.XPATH, "//td//a[contains(@href,'/people/')] | //a[contains(@href,'email')]")
            
#             if not links:
#                 return "No faculty profile links found. Page may use different structure."
            
#             # Get FRESH link (never stale)
#             try:
#                 link_elem = links[processed % len(links)]  # Round-robin safe
#                 href = link_elem.get_attribute('href')
#                 if not href or not '/people/' in href:
#                     processed += 1
#                     continue
                
#                 print(f"[{processed+1}] {href}")
                
#                 # STALE-SAFE CLICK
#                 for attempt in range(3):
#                     try:
#                         driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", link_elem)
#                         time.sleep(1)
#                         driver.execute_script("arguments[0].click();", link_elem)
#                         break
#                     except StaleElementReferenceException:
#                         print(f"  Stale link #{attempt+1} - refreshing...")
#                         links = find_faculty_links()  # REFRESH
#                         link_elem = links[processed % len(links)]
                
#                 # Wait for profile page
#                 wait.until(lambda d: '/people/' in d.current_url or d.current_url != base_url)
#                 time.sleep(3)
                
#                 # Extract email from PROFILE PAGE
#                 soup = BeautifulSoup(driver.page_source, 'html.parser')
#                 text = soup.get_text()
                
#                 # UMD email patterns
#                 EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,6}\b", re.I)
#                 emails = EMAIL_RE.findall(text)
                
#                 # [dot] obfuscation (from your attachment)
#                 dot_pat = r'([A-Za-z0-9._%+-]+)\[?\.?\[dot\]?([A-Za-z0-9.-]+)\[?\.?\[dot\]?([a-z]{2,})'
#                 for m in re.findall(dot_pat, text, re.I):
#                     emails.append(f"{m[0]}@{m[1]}.{m[2]}")
                
#                 new_emails = {e.lower() for e in emails if any(domain in e.lower() for domain in ['@umd.edu', '@cs.umd.edu'])}
#                 all_emails.update(new_emails)
                
#                 print(f"Emails: {len(new_emails)} | Total: {len(all_emails)}")
                
#                 # SAFE BACK
#                 driver.back()
#                 wait.until(lambda d: d.current_url == base_url)
#                 time.sleep(2)
                
#                 processed += 1
                
#             except Exception as e:
#                 print(f"Skip: {str(e)[:60]}")
#                 try:
#                     driver.back()
#                     wait.until(lambda d: d.current_url == base_url)
#                 except:
#                     pass
        
#         return f"""🎓 FACULTY EMAILS EXTRACTED
#                 ━━━━━━━━━━━━━━━━━━━━━━━━━━━
#                 ✅ Processed: {processed} profiles
#                 📧 Found: {len(all_emails)} unique emails

#                 {chr(10).join(f'• {email}' for email in sorted(all_emails))}"""
    
#     finally:
#         driver.quit()






# url = "https://www.cs.umd.edu/people/phonebook/faculty"
# result = scrape_faculty_profiles.invoke({"base_url": url})  # Pass as dict
# print(result)
