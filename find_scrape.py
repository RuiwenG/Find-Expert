"""
This script uses Selenium to scrape data from the website intro.co. 
It finds all profiles in different sections through navigating "show all"
buttons, and then collects Name and About information for each of the 
profiles, then it stores data in different CSV files that based on the 
section where the data came from.

"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv

options = Options()
options.add_argument("--no-sandbox")
options.add_argument("--headless")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
# Mimic windows to satisfy webpage (anti-scraping)
options.add_argument("--window-size=1920,1080")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")

# Update the path to ChromeDriver
service = Service('/usr/bin/chromedriver')
driver = webdriver.Chrome(options=options, service=service)
# Explicitly set timeout time to be 300
driver.set_page_load_timeout(300) 

url = "https://intro.co/marketplace"
driver.get(url)
wait = WebDriverWait(driver, 30)

button_selector = ".flex.w-full.h-full.items-center.justify-center.text-base"
initial_buttons = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, button_selector)))

# Create a set to contains scraped urls
scraped_profiles = set()

# Create CSV files
for i in range(len(initial_buttons)):
    # Re-fetch buttons to avoid stale element references after navigation
    wait.until(lambda d: d.execute_script("return document.readyState") == "complete") 
    buttons = driver.find_elements(By.CSS_SELECTOR, button_selector)
    button = buttons[i]
    
    # Create different CSV files based on different categories
    filename = f"profiles_{i}.csv"
    
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "About"])
        try:
            button.click()
            wait.until(EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, ".expert-card.w-full.cursor-pointer a")
            ))
            has_next_page = True
            while has_next_page:
                # wait till fully loaded
                profiles = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".expert-card.w-full.cursor-pointer a")))
                for profile in profiles:
                    try:
                        profile_link = profile.get_attribute("href")
                        # handle duplicate profiles
                        if profile_link in scraped_profiles:
                            continue
                        scraped_profiles.add(profile_link)
                        # Open the profile in a new tab
                        driver.execute_script(f"window.open('{profile_link}', '_blank');")
                        driver.switch_to.window(driver.window_handles[-1])  # Switch to the new tab
                        # Wait for the page to load. Might be duplicate, but for robust reason keep both
                        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
                        wait.until(
                            EC.presence_of_element_located(
                                (By.CSS_SELECTOR, ".md\\:max-w-\\[360px\\].lg\\:ml-20.md\\:ml-10")
                            )
                        )
                        # Scrape the data
                        name = driver.find_element(
                            By.CSS_SELECTOR, ".font-sofia.text-\\[26px\\].leading-\\[30px\\]"
                        ).text
                        about_element = wait.until(
                            EC.visibility_of_element_located(
                                (By.CSS_SELECTOR, 
                                '[class^="font-sofia text-\\[17px\\]"]')
                            )
                        )
                        # Write to CSV
                        writer.writerow([name, about_element.text])
                        # Close the current tab and switch back to the main tab
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])  # Back to the main tab

                    except Exception as e:
                        print(f"Error scraping profile: {e}")
                        # Ensure we close the tab if an error occurs
                        if len(driver.window_handles) > 1:
                            driver.close()
                            driver.switch_to.window(driver.window_handles[0])

                # Handle pagination
                try:
                    next_button = wait.until(EC.element_to_be_clickable(
                        (By.XPATH, "//button[contains(text(), 'More experts')]")
                    ))
                    next_button.click()
                    wait.until(EC.presence_of_all_elements_located(
                        (By.CSS_SELECTOR, ".expert-card.w-full.cursor-pointer a")
                    ))
                except Exception:
                    print("No more pages to load.")
                    has_next_page = False
            driver.back()
        except Exception as e:
            print(f"Error clicking button at index {i}: {e}")
  
driver.quit()
