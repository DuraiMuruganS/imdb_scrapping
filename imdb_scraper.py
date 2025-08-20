from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd, re, time
from datetime import datetime

URL = "https://www.imdb.com/chart/top/"

options = webdriver.ChromeOptions()
# options.add_argument("--headless")  # Use headless if needed

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get(URL)
time.sleep(4)

movies = []

# 1. Try classic table layout
rows = driver.find_elements(By.CSS_SELECTOR, "tbody.lister-list tr")
if rows:
    for idx, row in enumerate(rows, start=1):
        title = row.find_element(By.CSS_SELECTOR, "td.titleColumn a").text.strip()
        year = re.search(r"\d{4}", row.find_element(By.CSS_SELECTOR, "td.titleColumn span").text).group()
        rating = row.find_element(By.CSS_SELECTOR, "td.imdbRating strong").text.strip()
        movies.append([idx, title, int(year), float(rating)])
else:
    # 2. Fallback to modern card layout
    cards = driver.find_elements(By.CSS_SELECTOR, "li.ipc-metadata-list-summary-item")
    for idx, card in enumerate(cards, start=1):
        try:
            title_elem = card.find_element(By.CSS_SELECTOR, "h3")
            raw_title = title_elem.text.strip()
            title = re.sub(r"^\d+\.\s*", "", raw_title)

            # Extract year by regex if no span found
            text_block = card.text
            match = re.search(r"(19|20)\d{2}", text_block)
            year = int(match.group()) if match else None

            # Try both forms of rating span class
            rating = None
            try:
                rating_text = card.find_element(By.CSS_SELECTOR, "span.ipc-rating-star--rating").text.strip()
                rating = float(rating_text)
            except:
                try:
                    rating_text = card.find_element(By.CSS_SELECTOR, "span.ipc-rating-star__rating").text.strip()
                    rating = float(rating_text)
                except:
                    rating = None

            movies.append([idx, title, year, rating])
        except Exception as e:
            print(f"skipping card {idx}: {e}")

driver.quit()

df = pd.DataFrame(movies, columns=["Rank", "Title", "Year", "IMDb Rating"])
ts = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"imdb_top_250_{ts}.csv"
df.to_csv(filename, index=False, encoding="utf-8")
print(f"Saved {len(df)} movies to {filename}")