import psycopg2
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

# ⚠️ Replace with your secure connection string or use environment variables
DATABASE_URL = "postgresql://username:password@localhost:5432/r6_stat"

# 🧑‍🤝‍🧑 Player profiles and their target database tables
player_profiles = {
    "ymursi": {
        "url": "https://r6.tracker.network/r6siege/profile/xbl/ymursi/operators?playlist=ranked&season=37",
        "table": "ymursi_table"
    },
    "mkvbobo": {
        "url": "https://r6.tracker.network/r6siege/profile/xbl/mkvbobo/operators?playlist=ranked&season=37",
        "table": "bobo"
    },
    "oy9w": {
        "url": "https://r6.tracker.network/r6siege/profile/xbl/oy9w/operators?playlist=ranked&season=37",
        "table": "monkey"
    },
    "o captsleep": {
        "url": "https://r6.tracker.network/r6siege/profile/xbl/o%20captsleep/operators?playlist=ranked&season=37",
        "table": "captsleep_table"
    }
}

# 🌐 Selenium ChromeDriver setup (headless + incognito)
options = Options()
options.add_argument("--window-size=1920,1080")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--incognito")
options.add_argument("--headless")

# 🔧 Adjust ChromeDriver path as needed
service = Service("/usr/local/bin/chromedriver")
driver = webdriver.Chrome(service=service, options=options)

def scrape_and_update_db(player_name, profile):
    """Scrape operator stats for a player and update the corresponding database table."""
    url = profile["url"]
    table_name = profile["table"]

    print(f"\n🔍 Scraping data for: {player_name}\nURL: {url}")
    driver.get(url)
    time.sleep(7)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

    operator_data = []
    row_index = 1

    while True:
        try:
            base_xpath = f'//*[@id="app"]/div[2]/div[3]/div/main/div[3]/div[2]/div[3]/div/div/div/div[2]/div/div/div/div[{row_index}]'

            operator_name = driver.find_element(By.XPATH, f"{base_xpath}/div[1]/div/span").text.strip()
            rounds_played = int(driver.find_element(By.XPATH, f"{base_xpath}/div[2]/span/span").text)
            win_percentage = float(driver.find_element(By.XPATH, f"{base_xpath}/div[3]/span/span").text.replace("%", ""))
            kd_ratio = float(driver.find_element(By.XPATH, f"{base_xpath}/div[4]/span/span").text)

            data = (operator_name, rounds_played, win_percentage, kd_ratio)
            operator_data.append(data)

            print(f"✅ Row {row_index}: {data}")
            row_index += 1

        except Exception:
            print(f"⚠️ Finished scraping {player_name}. No more rows found.")
            break

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        # 📦 Create table if it doesn't exist
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                rounds_played INTEGER,
                win_percentage FLOAT,
                kd_ratio FLOAT,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # ♻️ Insert new data or update existing rows
        insert_query = f"""
            INSERT INTO {table_name} (name, rounds_played, win_percentage, kd_ratio, scraped_at)
            VALUES (%s, %s, %s, %s, NOW())
            ON CONFLICT (name) 
            DO UPDATE SET 
                rounds_played = EXCLUDED.rounds_played,
                win_percentage = EXCLUDED.win_percentage,
                kd_ratio = EXCLUDED.kd_ratio,
                scraped_at = NOW();
        """

        cursor.executemany(insert_query, operator_data)
        conn.commit()
        print(f"🎉 Updated `{table_name}` for {player_name} with {len(operator_data)} rows.")

    except Exception as e:
        print(f"❌ Database error for {player_name}: {e}")

    finally:
        cursor.close()
        conn.close()

# 🚀 Scrape and update all players
for player, profile in player_profiles.items():
    scrape_and_update_db(player, profile)

# 🧹 Close browser session
driver.quit()
print("\n✅ All player data scraped and stored successfully!")
