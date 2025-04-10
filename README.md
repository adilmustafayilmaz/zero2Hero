# Google Maps Location and Review Scraper

This application scrapes location links and their corresponding reviews from Google Maps based on a search URL.

## Functionality

1.  **`location_scrapper.py`**: Takes a Google Maps search URL and the number of times to scroll down the results page. It extracts the links to individual locations found in the search results and saves them into `location_links.csv`.
2.  **`review_scrapper2.py`**: Reads the location links from `location_links.csv`. For each location link, it navigates to the page, scrolls down the reviews section a specified number of times, extracts review data (reviewer name, rating, review text, etc.), and saves the reviews into a CSV file within a specified folder. It also saves the HTML source of the review page for potential debugging or further analysis.
3.  **`main.py`**: The main script that orchestrates the process. It defines the configuration parameters and calls the functions from the other two scripts in sequence.

## Configuration

All configuration is done within `main.py`:

*   `URL`: The Google Maps search URL you want to scrape locations from.
*   `NUM_OF_SCROLL_LOCATION`: How many times the script should simulate scrolling down on the search results page to load more locations. Increase this number to potentially find more locations.
*   `NUM_OF_SCROLL_REVIEW`: How many times the script should simulate scrolling down within the reviews section of each location page. Increase this number to scrape more reviews per location.
*   `FOLDER_NAME`: The name of the directory where the CSV files containing scraped reviews will be saved. Each location will have its own CSV file named after the location.
*   `HTML_FOLDER_NAME`: The name of the directory where the HTML source files of the review pages will be saved.

## How to Run

1.  **Install Dependencies**: Make sure you have the necessary Python libraries installed (e.g., `selenium`, `pandas`, `webdriver-manager`). You might need to install them using pip:
    ```bash
    pip install selenium pandas webdriver-manager beautifulsoup4
    ```
2.  **Configure `main.py`**: Open `main.py` and adjust the configuration variables (`URL`, `NUM_OF_SCROLL_LOCATION`, `NUM_OF_SCROLL_REVIEW`, `FOLDER_NAME`, `HTML_FOLDER_NAME`) as needed.
3.  **Run the Script**: Execute the main script from your terminal in the project directory:
    ```bash
    python main.py
    ```

## Output

*   **`location_links.csv`**: A CSV file containing the links to all scraped locations. This file is used as input for the review scraping step.
*   **`<FOLDER_NAME>/`**: This directory will contain individual CSV files for each location, holding the scraped review data.
*   **`<HTML_FOLDER_NAME>/`**: This directory will contain the raw HTML files for each location's review page.
```
