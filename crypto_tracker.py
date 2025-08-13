from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pandas as pd
import time
import os

# ==== SETTINGS ====
PRICE_THRESHOLD = 50000     # Show coins above this price
CHANGE_THRESHOLD = 5.0      # Show coins with more than +5% change in 24h
# ==================

# Selenium setup
options = Options()
options.add_argument("--headless")
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# Open CoinMarketCap
driver.get("https://coinmarketcap.com/")
time.sleep(5)  # Wait for page load

# Find table rows for top 10 coins
rows = driver.find_elements(By.XPATH, '//table/tbody/tr')[:10]

data = []
for row in rows:
    name = row.find_element(By.XPATH, './td[3]//p').text
    price_text = row.find_element(By.XPATH, './td[4]//span').text
    change_text = row.find_element(By.XPATH, './td[5]//span').text
    market_cap = row.find_element(By.XPATH, './td[8]//span').text

    # Convert price and change to numbers
    price = float(price_text.replace('$', '').replace(',', ''))
    change_24h = float(change_text.replace('%', '').replace(',', ''))

    data.append({
        "Name": name,
        "Price": price,
        "24h Change": change_24h,
        "Market Cap": market_cap
    })

driver.quit()

# Create DataFrame and add timestamp
df = pd.DataFrame(data)
df["Timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")

# Save to CSV (append if exists)
file_name = "crypto_data.csv"
df.to_csv(file_name, mode='a', index=False, header=not os.path.exists(file_name))

print(" Data saved to", file_name)

# === FILTERING ===
filtered_df = df[(df["Price"] > PRICE_THRESHOLD) & (df["24h Change"] > CHANGE_THRESHOLD)]

print("\n Coins matching filter:")
if not filtered_df.empty:
    print(filtered_df.to_string(index=False))
else:
    print("No coins match the filter criteria.")
