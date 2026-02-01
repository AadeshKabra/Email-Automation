from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time


class BrowserSession():
    def __init__(self):
        self.driver = self._init_driver()
        self.current_url = None
        self.history = []

    
    def _init_driver(self):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.implicitly_wait(10)
        return driver

    
    def navigate(self, url):
        self.driver.get(url)
        WebDriverWait(self.driver, 15).until(
            lambda a: a.execute_script("return document.readyState") == "complete"
        )
        self.current_url = url
        self.history.append(url)
        return f"Navigated to {url}"
    

    def get_page_content(self):
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        for element in soup(['script', 'style', 'nav', 'footer', 'header']):
            element.decompose()

        text = soup.get_text(separator="\n", strip=True)
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        clean_text = '\n'.join(lines)

        return clean_text
    

    def get_all_links(self):
        links = []
        elements = self.driver.find_elements(By.TAG_NAME, "a")
        for elem in elements:
            href = elem.get_attribute('href')
            text = elem.text.strip()
            if href and text and len(text)>0:
                links.append({"Text": text, "Url": href})

        return links
    

    def click_links(self, link_url):
        self.driver.get(link_url)

        WebDriverWait(self.driver, 15).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        time.sleep(2)

        self.current_url = link_url
        self.history.append(link_url)
        return f"Clicked and navigated to {link_url}"
    

    def close(self):
        self.driver.quit()

    
    def get_current_url(self):
        return self.current_url


    def get_history(self):
        return self.history
