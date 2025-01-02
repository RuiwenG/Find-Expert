# This is the file that scrapes the data from the website intro.co

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import csv
import time

options = Options()
# options.add_argument("--headless")
options.add_argument("--no-sandbox")
# options.binary_location = "/usr/bin/google-chrome-stable"
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
# options.add_argument(f"crash-dumps-dir={os.path.expanduser('~/tmp/Crashpad')}")
# options.add_argument("--remote-debugging-port=9222")

# Update the path to ChromeDriver
service = Service('/usr/bin/chromedriver')
driver = webdriver.Chrome(options=options, service=service)

url = "https://intro.co/marketplace"
driver.get(url)
wait = WebDriverWait(driver, 30)
print(driver.page_source)

try:
    wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")
    buttons = wait.until(
    EC.presence_of_all_elements_located(
        # this part was inspected manually
        (    By.XPATH,
            "//button[contains(@class, 'flex w-full h-full items-center justify-center text-base')]//span[.='See all']",
        )))
    
    print(f"Found {len(buttons)} buttons.")
    driver.save_screenshot("debug_screenshot2.png")

except Exception as e:
    print(f"An error occurred: {e}")
    driver.save_screenshot("debug_screenshot1.png")
    
# create a CSV file to store the data
with open("profiles.csv", mode="w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Name", "About"])
    for button in buttons:
        try:
            button.click()
            # make sure the page has been loaded correctly
            time.sleep(2)
            while True:
                # find all the profiles with link on the current webpage
                profiles = driver.find_elements(
                    By.CSS_SELECTOR, ".expert-card.w-full.cursor-pointer a"
                )
                for profile in profiles:
                    try:
                        profile.click()
                        wait.until(
                            EC.presence_of_element_located(
                                (
                                    By.CLASS_NAME,
                                    "md:max-w-[360px] lg:ml-20 md:ml-10",
                                )
                            )
                        )
                        name = driver.find_element(
                            By.CLASS_NAME, "font-sofia text-[26px] leading-[30px]"
                        ).text
                        about = driver.find_element(
                            By.CLASS_NAME,
                            "font-sofia text-[17px] font-light leading-6 tracking-[-0.25px] text-charcoal whitespace-pre-wrap pt-2 cropped",
                        ).text
                        print(f"Name: {name}, About: {about}, Length: {len(name)}")
                        driver.back()  # Go back to the profile list
                        wait.until(
                            EC.presence_of_all_elements_located(
                                (
                                    By.CSS_SELECTOR,
                                    ".expert-card.w-full.cursor-pointer a",
                                )
                            )
                        )
                        # wrties to the CSV file
                        writer.writerow([name, about])

                    except Exception as e:
                        print(f"Error clicking profile: {e}")

                try:
                    continue_button = driver.find_element(
                        By.XPATH, "//button[contains(text(), 'More experts')]"
                    )  # Update XPath for the "more experts" button
                    continue_button.click()
                    time.sleep(2)  # Adjust as needed
                except:
                    print("No more pages to load.")
                    break  # Exit pagination loop when no "continue" button is found

        except Exception as e:
            print(f"Error clicking button: {e}")


driver.quit()
