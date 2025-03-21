# Rainbow Six Siege Operator Stats Scraper

🎮 A Python-based web scraper that pulls operator statistics from [r6.tracker.network](https://r6.tracker.network) for multiple Xbox Live profiles and stores them in a PostgreSQL database. Designed for data analysis, dashboards, or historical stat tracking.

## 🔧 Tech Stack

- **Python 3.13**
- **Selenium** (headless browser automation)
- **PostgreSQL + psycopg2**
- **ChromeDriver**

## 🚀 Features

- Scrapes **operator-specific stats** (rounds played, win rate, K/D) for specified players.
- Tags each operator as either an **Attacker** or **Defender** based on Rainbow Six Siege Year 10 Season 1 classification.
- Supports **multiple player profiles** with custom database tables.
- Automatically creates or updates database entries without duplicating data.
- Designed for automation (e.g., CRON job ready via headless mode).

## 📁 Project Structure

```bash
r6_scraper_auto.py        # Main script to scrape and update all player tables
README.md                 # You are here
