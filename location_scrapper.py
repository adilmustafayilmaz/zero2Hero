from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import pandas as pd
import time



def locationScrapper(map_url, number_of_scroll):
    # Chrome WebDriver başlat
    service = Service(executable_path="chromedriver.exe")  # Dosya yolunu kendi bilgisayarına göre düzenle
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(service=service, options=options)


    NUMBER_OF_SCROLL = number_of_scroll
    # Google Maps URL'si
    url = map_url




    driver.get(url)

    # Sayfanın yüklenmesini bekle
    time.sleep(4)

    # Soldaki scroll edilebilir bölgeyi bul
    scrollable_div = driver.find_element(By.XPATH, '//div[@role="feed"]')

    # 4 kez aşağı kaydır
    for _ in range(NUMBER_OF_SCROLL):
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollTop + arguments[0].offsetHeight;", scrollable_div)
        time.sleep(2)

    # Lokasyon kartlarını topla
    time.sleep(2)  # Scroll sonrası yeni içerik yüklenmesi için bekle
    cards = driver.find_elements(By.XPATH, '//a[contains(@href, "/place/")]')

    # Linkleri al ve filtrele
    links = []
    for card in cards:
        href = card.get_attribute("href")
        if href and "/place/" in href:
            links.append(href)

    # Yinelenenleri kaldır
    links = list(set(links))

    # CSV dosyasına kaydet
    df = pd.DataFrame(links, columns=["Location Link"])
    df.to_csv("location_links.csv", index=False, encoding="utf-8-sig")

    print(f"{len(links)} link kaydedildi.")

    # Tarayıcıyı kapat
    driver.quit()

    return True
