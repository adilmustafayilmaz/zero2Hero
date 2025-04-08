import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup


def scrape_yorumlar_and_save_csv(url, output_file="yorumlar.csv"):
    # Setup Chrome
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    # chrome_options.add_argument("--headless")  # Uncomment for background run

    service = Service(executable_path="chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get(url)

        # Step 1: Click the 'Yorumlar' button
        containers = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".bJzME.tTVLSc"))
        )

        yorumlar_clicked = False
        for container in containers:
            buttons = container.find_elements(By.TAG_NAME, "button")
            for button in buttons:
                if "Yorumlar" in button.text:
                    button.click()
                    print("Clicked on 'Yorumlar'")
                    yorumlar_clicked = True
                    break
            if yorumlar_clicked:
                break

        if not yorumlar_clicked:
            print("Couldn't find 'Yorumlar' button.")
            return

        time.sleep(1)

        # Step 2: Wait for review scroll container
        scroll_container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".m6QErb.DxyBCb.kA9KIf.dS8AEf.XiKgde")
            )
        )

        # Step 3: Scroll down multiple times
        for i in range(2):
            driver.execute_script(
                "arguments[0].scrollTop = arguments[0].scrollHeight", scroll_container
            )
            print(f"Scrolled {i+1}/4")
            time.sleep(2)

        # Step 4: Expand all reviews by clicking 'w8nwRe kyuRq' buttons
        expand_buttons = driver.find_elements(By.CSS_SELECTOR, ".w8nwRe.kyuRq")
        print(f"Found {len(expand_buttons)} expandable review buttons.")
        for i, btn in enumerate(expand_buttons):
            try:
                driver.execute_script("arguments[0].click();", btn)
                time.sleep(0.2)
            except Exception as e:
                print(f"Could not click expand button #{i}: {e}")

        time.sleep(2)

        # Step 5: Collect full reviews
        review_elements = driver.find_elements(By.CSS_SELECTOR, ".jftiEf.fontBodyMedium")

        with open("reviews.csv", mode="w", newline='', encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(['Username', 'Rating', 'Review'])  # Header
            for element in review_elements:
                html = element.get_attribute('innerHTML')
                soup = BeautifulSoup(html, 'html.parser')
                username = soup.find('div', class_='d4r55')
                rating = soup.find('span', class_='fzvQIb')
                print(rating)
                review_text = soup.find('span', class_='wiI7pd')

                username_text = username.get_text(strip=True) if username else ''
                rating_text = rating.get_text(strip=True) if rating else ''
                review_text_text = review_text.get_text(strip=True) if review_text else ''
                writer.writerow([username_text, rating_text, review_text_text])

            print("✅ Data successfully saved to reviews.csv")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        driver.quit()

# Example usage
scrape_yorumlar_and_save_csv("https://www.google.com/maps/place/Olea+Otel/@36.7161891,37.1104029,17z/data=!4m10!3m9!1s0x152fce1b1f01923f:0xc947ec11a420a70!5m3!1s2025-04-08!4m1!1i2!8m2!3d36.7161848!4d37.1129778!16s%2Fg%2F11b6wjf1p_?authuser=0&hl=tr&entry=ttu&g_ep=EgoyMDI1MDQwMi4xIKXMDSoASAFQAw%3D%3D", "yorumlar.csv")
