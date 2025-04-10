import location_scrapper
import review_scrapper2
import time


URL="https://www.google.com/maps/search/otel+near+%C5%9Eanl%C4%B1urfa/@37.1571649,38.7771913,15z/data=!3m1!4b1!4m4!2m3!5m2!5m1!1s2025-04-09?entry=ttu&g_ep=EgoyMDI1MDQwNy4wIKXMDSoASAFQAw%3D%3D" # Google Maps URL
NUM_OF_SCROLL_LOCATION=40 # Number of scrolls for location links
NUM_OF_SCROLL_REVIEW=40 # Number of scrolls for reviews
FOLDER_NAME = 'Şanlıurfa_Otel' # Folder to save CSV files
HTML_FOLDER_NAME = 'HTML_Reviews_Şanlıurfa_Otel' # Folder to save HTML files

# DO NOT CHANGE THIS
csv_path = "location_links.csv"


if __name__ == "__main__":
    location_scrapper.locationScrapper(URL, NUM_OF_SCROLL_LOCATION) # Scrape location links from Google Maps

    print("Location links scraped successfully.")

    time.sleep(2) # Wait for 2 seconds

    location_links = review_scrapper2.get_location_links(csv_path) # Get location links from CSV file

    i = 0
    for link in location_links:
        review_scrapper2.scrape_reviews_and_save_csv(link, NUM_OF_SCROLL_REVIEW, FOLDER_NAME, HTML_FOLDER_NAME) # Scrape reviews and save to CSV and HTML files
        i += 1
    