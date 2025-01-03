# This is the file that scrapes the data from the website intro.co

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

options.add_argument("--window-size=1920,1080")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")


# Update the path to ChromeDriver
service = Service('/usr/bin/chromedriver')
driver = webdriver.Chrome(options=options, service=service)

url = "https://intro.co/marketplace"
driver.get(url)
wait = WebDriverWait(driver, 30)

print(driver.title)

# Open the "See all" section
try:
    wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")
    # updates the button
    buttons = wait.until(EC.presence_of_all_elements_located(
        (By.CSS_SELECTOR, ".flex.w-full.h-full.items-center.justify-center.text-base")
    ))
    print(f"Found {len(buttons)} buttons.")
except Exception as e:
    print(f"Error finding 'See all' buttons: {e}")
    driver.quit()
    exit()

# create a set to contains scraped urls
scraped_profiles = set()

# Create CSV file
with open("profiles.csv", mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Name", "About"])

    for button in buttons:
        try:
            button.click()
            wait.until(EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, ".expert-card.w-full.cursor-pointer a")
            ))

            while True:
                profiles = driver.find_elements(By.CSS_SELECTOR, ".expert-card.w-full.cursor-pointer a")
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
                        # DD
                        print(profile_link)
                        # Wait for the page to load
                        wait.until(
                            EC.presence_of_element_located(
                                (By.CSS_SELECTOR, ".md\\:max-w-\\[360px\\].lg\\:ml-20.md\\:ml-10")
                            )
                        )
                        # Scrape the data
                        name = driver.find_element(
                            By.CSS_SELECTOR, ".font-sofia.text-\\[26px\\].leading-\\[30px\\]"
                        ).text
                        print(f"Scraped: {name}")
                        # ACTION
                        # need to wait, some content are dynamically loaded.
                        about_element = wait.until(
                            EC.visibility_of_element_located(
                                (By.CSS_SELECTOR, 
                                '[class^="font-sofia text-\\[17px\\]"]')
                            )
                        )
                        about_bol = wait.until(lambda d: about_element.text.strip() != "")
                        if not about_bol:
                            print("oh no!")
                        else:
                            print(2)
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
                            print(driver.title)

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
                    break
        except Exception as e:
            print(f"Error clicking button: {e}")

driver.quit()
