from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

def scrape_unusual_options_selenium():
    # Set up Chrome options for headless mode (optional)
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in background
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Initialize the driver (ensure chromedriver is in PATH or specify path)
    #service = Service('/path/to/chromedriver')
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        url = 'https://stocknear.com/'
        driver.get(url)
        
        # Wait for the page to load dynamically
        wait = WebDriverWait(driver, 10)
        
        # Wait for the "Unusual Options Orders" section or link to appear
        unusual_link = wait.until(EC.presence_of_element_located((By.LINK_TEXT, "Unusual Options Orders")))
        
        # Find the table after the link (adjust selector if needed)
        table = unusual_link.find_element(By.XPATH, "following::table[1]")
        
        # Extract rows from table body
        rows = table.find_elements(By.TAG_NAME, "tr")[1:]  # Skip header
        
        data = []
        for row in rows:
            cols = row.find_elements(By.TAG_NAME, "td")
            if len(cols) < 4:
                continue
            
            # Symbol (with link)
            symbol_cell = cols[0]
            symbol_link = symbol_cell.find_element(By.TAG_NAME, "a")
            symbol = symbol_link.text.strip()
            symbol_href = symbol_link.get_attribute("href")
            full_url = 'https://stocknear.com' + symbol_href if symbol_href.startswith('/') else symbol_href
            
            # Type (Puts/Calls)
            typ = cols[1].text.strip()
            
            # Premium
            prem = cols[2].text.strip()
            
            # Strike
            strike = cols[3].text.strip()
            
            data.append({
                'symbol': symbol,
                'type': typ,
                'premium': prem,
                'strike': strike,
                'url': full_url
            })
        
        return data
    
    finally:
        driver.quit()

# Example usage
if __name__ == '__main__':
    try:
        results = scrape_unusual_options_selenium()
        for item in results:
            print(item)
    except Exception as e:
        print(f"Error: {e}")
