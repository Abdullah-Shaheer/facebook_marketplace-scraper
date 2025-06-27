# 📱 FB Marketplace Price Scraper

A powerful Python-based scraper that fetches data from Facebook Marketplace for high-demand Apple devices like iPhones (iPhone 11 and newer), Apple Watch Ultra, MacBook Pro M4, and MacBook Air M4. It then compares the listed price with the current buy-back price from [MusicMagpie UK](https://www.musicmagpie.co.uk/start-selling), and alerts the user via Telegram if a deal is found within the defined threshold.

---

## 🚀 Features

- ✅ Scrapes **Facebook Marketplace** listings using Selenium.
- ✅ Filters out:
  - Sellers who joined after **2022**.
  - Listings **older than 24 hours**.
  - Listings priced below **£200** to avoid scams.
- ✅ Extracts detailed information from matched listings.
- ✅ Fetches current price for the same model from **MusicMagpie**.
- ✅ If the Facebook price is **≤ 25%** of the MusicMagpie price, sends a **Telegram alert** with full ad details.
- ✅ Avoids duplicate alerts by keeping a log of previously alerted links.

---

## 🛠️ Technologies Used

- Python
- Selenium WebDriver
- Undetected Chromedriver
- BeautifulSoup (bs4)
- Traceback
- OS module
- urllib
- Regular Expressions (regex)
- Telegram Bot API

## 📋 How It Works

1. Launches a headless browser and navigates to Facebook Marketplace.
2. Applies predefined filters to find relevant listings:
   - Device type (iPhones, Apple Watch Ultra, MacBooks M4)
   - Seller joined year ≤ 2022
   - Posted in the last 24 hours
   - Price ≥ £200
3. For each qualified ad:
   - Fetches detailed product info (price, storage, seller info).
   - Navigates to **MusicMagpie**, searches the device model, retrieves current offer price.
4. Compares both prices:
   - If Facebook ad price is a **good deal (≤ 25% of MM price)**, sends a Telegram alert to the user.
   - Otherwise, skips the ad.
5. Keeps track of previously alerted ads in a local file to avoid duplicate alerts.

---

## 📬 Telegram Alerts

If a match is found based on the criteria:
- You will receive an **instant Telegram message** with:
  - The device name and storage
  - Facebook ad price
  - MusicMagpie comparison price
  - A direct link to the Facebook ad

---

## ⚙️ Prerequisites

- Python 3.7+
- Google Chrome
- ChromeDriver (matching your Chrome version)

Install required packages:

```bash
pip install -r requirements.txt
