import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup
import pandas as pd
import os

NUMBER_OF_SCROLL = 25
csv_file = "location_links.csv"
FOLDER_NAME = 'Kilis_Restoran'

def scrape_yorumlar_and_save_csv(url, output_file="yorumlar.csv"):
    # Setup Chrome
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    # chrome_options.add_argument("--headless")  # Uncomment for background run

    service = Service(executable_path="chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get(url)

        element = driver.find_element(By.CSS_SELECTOR, "h1.DUwDvf.lfPIob")

        # İçindeki metni al ve bir değişkene ata
        baslik = element.text
        baslik = baslik.replace(" ", "_")
        baslik = baslik + "_reviews" + ".csv" 

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
        for i in range(NUMBER_OF_SCROLL):
            driver.execute_script(
                "arguments[0].scrollTop = arguments[0].scrollHeight", scroll_container
            )
            print(f"Scrolled {i+1}/" + str(NUMBER_OF_SCROLL))
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

        # Create folder and add csv file to that folder
        os.makedirs(FOLDER_NAME, exist_ok=True)
        baslik = os.path.join(FOLDER_NAME, baslik)

        with open(baslik, mode="w", newline='', encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(['Username', 'Rating', 'Review'])  # Header
            for element in review_elements:
                html = element.get_attribute('innerHTML')
                soup = BeautifulSoup(html, 'html.parser')
                username = soup.find('div', class_='d4r55')
                rating = soup.find('span', class_='fzvQIb')
                review_text = soup.find('span', class_='wiI7pd')

                username_text = username.get_text(strip=True) if username else ''
                rating_text = rating.get_text(strip=True) if rating else ''
                review_text_text = review_text.get_text(strip=True) if review_text else ''
                writer.writerow([username_text, rating_text, review_text_text])

            print("✅ Data successfully saved to " + baslik)

    except Exception as e:
        print(f"Error: {e}")

    finally:
        driver.quit()


def get_location_links(csv_path):
    """
    Reads a CSV file with a 'Location Link' column and returns a list of links.
    
    Parameters:
        csv_path (str): The path to the CSV file.
    
    Returns:
        list: A list of all location links.
    """
    df = pd.read_csv(csv_path)

    # Check if the expected column exists
    if "Location Link" not in df.columns:
        raise ValueError("The CSV file must contain a 'Location Link' column.")

    links = df["Location Link"].dropna().tolist()
    return links


if __name__ == "__main__":
    location_links = get_location_links(csv_file)
    i = 0
    for link in location_links:
        scrape_yorumlar_and_save_csv(link, ("review" + str(i) + ".csv"))
        i += 1
