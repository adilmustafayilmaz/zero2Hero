import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def scrape_yorumlar_and_save_csv(url, output_file="yorumlar.csv"):
    # Chrome setup
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    # chrome_options.add_argument("--headless")  # Optional headless mode

    service = Service(executable_path="chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get(url)

        # Step 1: Click 'Yorumlar'
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

        # Step 2: Wait for scrollable container
        scroll_container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".m6QErb.DxyBCb.kA9KIf.dS8AEf.XiKgde")
            )
        )

        # Step 3: Scroll down 4 times
        for i in range(4):
            driver.execute_script(
                "arguments[0].scrollTop = arguments[0].scrollHeight", scroll_container
            )
            print(f"Scrolled {i+1}/4")
            time.sleep(2)

        # Step 4: Click all "Daha fazla" to expand full reviews
        daha_fazla_elements = driver.find_elements(By.XPATH, "//span[text()='Daha fazla']")
        print(f"Found {len(daha_fazla_elements)} 'Daha fazla' elements.")
        for i, elem in enumerate(daha_fazla_elements):
            try:
                driver.execute_script("arguments[0].click();", elem)
                time.sleep(0.2)  # slight delay between clicks
            except Exception as e:
                print(f"Couldn't click 'Daha fazla' #{i}: {e}")

        time.sleep(1)

        # Step 5: Collect all reviews
        review_elements = driver.find_elements(By.CSS_SELECTOR, ".jftiEf.fontBodyMedium")
        reviews = [el.text.strip() for el in review_elements if el.text.strip() != ""]

        print(f"\n✅ Collected {len(reviews)} full reviews.")

        # Step 6: Save to CSV
        with open(output_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Review"])
            for review in reviews:
                writer.writerow([review])

        print(f"✅ Saved to {output_file}")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        driver.quit()

# Example usage
scrape_yorumlar_and_save_csv("https://www.google.com/maps/place/Olea+Otel/@36.7161891,37.1104029,17z/data=!4m10!3m9!1s0x152fce1b1f01923f:0xc947ec11a420a70!5m3!1s2025-04-08!4m1!1i2!8m2!3d36.7161848!4d37.1129778!16s%2Fg%2F11b6wjf1p_?authuser=0&hl=tr&entry=ttu&g_ep=EgoyMDI1MDQwMi4xIKXMDSoASAFQAw%3D%3D", "yorumlar.csv")
