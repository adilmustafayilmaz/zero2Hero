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
import codecs
import re


csv_file = "location_links.csv" # Path to the CSV file containing location links # Folder to save CSV files


def scrape_reviews_and_save_csv(url, NUMBER_OF_SCROLL, FOLDER_NAME, HTML_FOLDER_NAME):
    # Setup Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    # chrome_options.add_argument("--headless")  # Uncomment for background run

    service = Service(executable_path="chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get(url)

        element = driver.find_element(By.CSS_SELECTOR, "h1.DUwDvf.lfPIob")

        # İçindeki metni al ve bir değişkene ata
        baslik = element.text
        baslik = baslik.replace(" ", "_")
        csv_filename = baslik + "_reviews" + ".csv" 
        html_filename = baslik + "_reviews" + ".html"

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
            time.sleep(1)

        # Step 4: Expand all reviews by clicking 'w8nwRe kyuRq' buttons
        expand_buttons = driver.find_elements(By.CSS_SELECTOR, ".w8nwRe.kyuRq")
        print(f"Found {len(expand_buttons)} expandable review buttons.")
        for i, btn in enumerate(expand_buttons):
            try:
                driver.execute_script("arguments[0].click();", btn)
                time.sleep(0.2)
            except Exception as e:
                print(f"Could not click expand button #{i}: {e}")

        time.sleep(1)

        # Step 5: Collect full reviews
        review_elements = driver.find_elements(By.CSS_SELECTOR, ".jftiEf.fontBodyMedium")

        # Create CSV folder and add csv file to that folder
        os.makedirs(FOLDER_NAME, exist_ok=True)
        csv_path = os.path.join(FOLDER_NAME, csv_filename)

        # Create HTML folder for pretty HTML output
        os.makedirs(HTML_FOLDER_NAME, exist_ok=True)
        html_path = os.path.join(HTML_FOLDER_NAME, html_filename)

        # Save reviews to CSV
        with open(csv_path, mode="w", newline='', encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(['Username', 'Rating', 'Review', 'Photo_Links'])  # Header with Photo_Links
            for element in review_elements:
                html = element.get_attribute('innerHTML')
                soup = BeautifulSoup(html, 'html.parser')
                username = soup.find('div', class_='d4r55')
                
                # Extract rating - try both methods
                rating_value = 0
                rating_text = "No rating"
                
                # Method 1: Check for numeric ratings (e.g., "5/5")
                rating_numeric = soup.find('span', class_='fzvQIb')
                if rating_numeric and rating_numeric.text.strip():
                    rating_text = rating_numeric.text.strip()
                    # Extract number from rating like "5/5"
                    if '/' in rating_text:
                        try:
                            rating_value = float(rating_text.split('/')[0])
                        except ValueError:
                            rating_value = 0
                
                # Method 2: Check for star ratings if no numeric rating
                if rating_value == 0:
                    star_rating_element = soup.find('span', class_='kvMYJc')
                    if star_rating_element:
                        # Count the number of filled stars
                        filled_stars = star_rating_element.find_all('span', class_=lambda cls: cls and 'elGi1d' in cls)
                        if filled_stars:
                            rating_value = len(filled_stars)
                            rating_text = f"{rating_value} stars"
                
                review_text = soup.find('span', class_='wiI7pd')
                
                # Extract photo links
                photo_links = []
                photo_elements = soup.find_all('button', class_='Tya61d')
                for photo_el in photo_elements:
                    style_attr = photo_el.get('style', '')
                    img_url_match = re.search(r'url\("([^"]+)"\)', style_attr)
                    if img_url_match:
                        photo_links.append(img_url_match.group(1))

                username_text = username.get_text(strip=True) if username else ''
                review_text_text = review_text.get_text(strip=True) if review_text else ''
                
                # Join all photo links with comma for CSV
                photo_links_text = ", ".join(photo_links) if photo_links else ''
                
                writer.writerow([username_text, rating_text, review_text_text, photo_links_text])

            print("✅ Data successfully saved to " + csv_path)
        
        # Save reviews as pretty HTML
        with codecs.open(html_path, 'w', encoding='utf-8') as html_file:
            # Create HTML structure with styling
            html_content = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{baslik} - Reviews</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f8f9fa; }}
        h1 {{ color: #1a73e8; }}
        .review-container {{ 
            margin-bottom: 20px; 
            padding: 15px; 
            border-radius: 8px; 
            background-color: white; 
            box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24); 
        }}
        .username {{ 
            font-weight: bold; 
            font-size: 16px; 
            color: #202124; 
            margin-bottom: 5px; 
        }}
        .rating {{ 
            color: #e7711b; 
            margin-bottom: 8px; 
            font-weight: bold; 
        }}
        .review-text {{ line-height: 1.5; }}
        .original-html {{ 
            margin-top: 15px; 
            border-top: 1px solid #dadce0; 
            padding-top: 10px; 
            font-family: monospace; 
        }}
        .stars {{
            color: #e7711b;
            font-size: 20px;
            letter-spacing: 3px;
        }}
        .photo-gallery {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 15px;
        }}
        .review-photo {{
            width: 150px;
            height: 150px;
            object-fit: cover;
            border-radius: 4px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.12);
        }}
    </style>
</head>
<body>
    <h1>{baslik} - Reviews</h1>
    <p>Total reviews collected: {len(review_elements)}</p>
    <div class="reviews">
'''
            
            # Add each review
            for i, element in enumerate(review_elements):
                html = element.get_attribute('innerHTML')
                soup = BeautifulSoup(html, 'html.parser')
                username = soup.find('div', class_='d4r55')
                
                # Extract rating - try both methods
                rating_value = 0
                rating_display = ""
                rating_text = ""
                
                # Method 1: Check for numeric ratings (e.g., "5/5")
                rating_numeric = soup.find('span', class_='fzvQIb')
                if rating_numeric and rating_numeric.text.strip():
                    rating_text = rating_numeric.text.strip()
                    # Extract number from rating like "5/5"
                    if '/' in rating_text:
                        try:
                            rating_value = float(rating_text.split('/')[0])
                            max_rating = float(rating_text.split('/')[1])
                            # Show stars based on the rating
                            stars_html = "★" * int(rating_value) + "☆" * int(max_rating - rating_value)
                            rating_display = f"<span class='stars'>{stars_html}</span> {rating_text}"
                        except (ValueError, IndexError):
                            rating_display = rating_text
                    else:
                        rating_display = rating_text
                
                # Method 2: Check for star ratings if no numeric rating was found
                if not rating_display:
                    star_rating_element = soup.find('span', class_='kvMYJc')
                    if star_rating_element:
                        # Count the number of filled stars
                        filled_stars = star_rating_element.find_all('span', class_=lambda cls: cls and 'elGi1d' in cls)
                        if filled_stars:
                            rating_value = len(filled_stars)
                            stars_html = "★" * rating_value + "☆" * (5 - rating_value)
                            rating_display = f"<span class='stars'>{stars_html}</span> {rating_value} stars"
                        else:
                            rating_display = "No rating"
                    else:
                        rating_display = "No rating"
                
                review_text = soup.find('span', class_='wiI7pd')
                
                # Extract photo links
                photo_links = []
                photo_elements = soup.find_all('button', class_='Tya61d')
                for photo_el in photo_elements:
                    style_attr = photo_el.get('style', '')
                    img_url_match = re.search(r'url\("([^"]+)"\)', style_attr)
                    if img_url_match:
                        photo_links.append(img_url_match.group(1))

                username_text = username.get_text(strip=True) if username else 'Anonymous'
                review_text_text = review_text.get_text(strip=True) if review_text else 'No review text'
                
                # Pretty format the original HTML
                pretty_html = BeautifulSoup(html, 'html.parser').prettify()
                
                # Add photo gallery HTML if photos exist
                photo_gallery_html = ""
                if photo_links:
                    photo_gallery_html = '<div class="photo-gallery">'
                    for photo_url in photo_links:
                        photo_gallery_html += f'<a href="{photo_url}" target="_blank"><img class="review-photo" src="{photo_url}" alt="Review photo" /></a>'
                    photo_gallery_html += '</div>'
                
                html_content += f'''
        <div class="review-container">
            <div class="username">Review #{i+1}: {username_text}</div>
            <div class="rating">{rating_display}</div>
            <div class="review-text">{review_text_text}</div>
            {photo_gallery_html}
            <details>
                <summary>Show original HTML</summary>
                <pre class="original-html">{pretty_html}</pre>
            </details>
        </div>
'''
            
            # Close HTML tags
            html_content += '''
    </div>
</body>
</html>
'''
            html_file.write(html_content)
            
            print(f"✅ HTML reviews successfully saved to {html_path}")

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