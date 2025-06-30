from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException
import re
import requests
import traceback
import undetected_chromedriver as uc
import os
from urllib.parse import urlparse


def normalize_fb_link(link):
    """
    Returns the Facebook listing URL stripped of query parameters.
    e.g. 'https://www.facebook.com/marketplace/item/1234567890/?ref=...'
    becomes 'https://www.facebook.com/marketplace/item/1234567890'
    """
    parsed = urlparse(link)
    return parsed.scheme + "://" + parsed.netloc + parsed.path


def check_fb_location(driver):
    try:
        TARGET_LOCATIONS = [
            "leicester", "hinckley", "nuneaton", "lutterworth", "coventry", "rugby", "tamworth", "atherstone",
            "coalville", "swadlincote", "ashby", "burton upon trent", "derby", "loughborough", "nottingham",
            "mansfield", "newark on trent", "grantham", "meton mowbray", "peterborough", "oakham",
            "market harborough", "kettering", "wellingborough", "corby", "northampton", "daventry",
            "leamington spa", "bedworth", "sutton coldfield"
        ]

        spans = WebDriverWait(driver, 10).until(
            ec.presence_of_all_elements_located(
                (By.XPATH, "//span[@class='x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x6prxxf xvq8zen x1s688f xzsf02u']")
            )
        )

        if len(spans) >= 2:
            location_text = spans[1].text.strip().lower()
            for loc in TARGET_LOCATIONS:
                if loc in location_text:
                    print(f"Location:- {location_text}")
                    return True
                else:
                    print(f"Location not in the list: {location_text}")
        return False

    except Exception as e:
        print(f"Error checking location: {e}")
        return False


def send_telegram_alert(message):
    token = 'your_token'
    chat_id = 'your_chat_id'
    url = f'https://api.telegram.org/bot{token}/sendMessage'

    payload = {
        'chat_id': chat_id,
        'text': message
    }

    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"❌ Failed to send Telegram alert: {e}")


def set_up_driver():
    options = uc.ChromeOptions()
    # service = Service("chromedriver.exe")
    # options.debugger_address = "localhost:9222"
    # options.binary_location = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
    # user_data_dir = "C:\\Users\\CMP\\AppData\\Local\\Google\\Chrome\\User Data\\Profile 1"
    options.add_argument(r'--user-data-dir=C:\Chromeprofiles\profile1clone')
    options.add_argument("--disable-renderer-backgrounding")
    options.add_argument("--disable-backgrounding-occluded-windows")
    options.add_argument('--disable-blink-features=AutomationControlled')
    d = uc.Chrome(options=options)
    return d


def facebook_login(driver, email, password):
    driver.get("https://www.facebook.com/")

    try:
        time.sleep(2)
        email_input = WebDriverWait(driver, 30).until(ec.presence_of_element_located((By.ID, "email")))
        if email_input:
            email_input.send_keys(email)

        password_input = WebDriverWait(driver, 30).until(ec.presence_of_element_located((By.ID, "pass")))
        password_input.send_keys(password)
        password_input.send_keys(Keys.RETURN)
        time.sleep(5)

        print("Login attempted. Check browser.")
    except Exception as e:
        print("Error during login:", e)
    # driver.quit()  # Close browser after testing


def market_place(driver, name):
    urls = []

    driver.get(f"https://www.facebook.com/marketplace/110212755674509/search?minPrice=200&daysSinceListed=1&query={name}")
    time.sleep(5)
    driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
    time.sleep(5)
    try:
        WebDriverWait(driver, 10).until(ec.presence_of_all_elements_located((By.XPATH, "//div[@class='x9f619 x78zum5 x1r8uery xdt5ytf x1iyjqo2 xs83m0k x1e558r4 x150jy0e x1iorvi4 xjkvuk6 xnpuxes x291uyu x1uepa24']")))
    except:
        print('There are no listings found. So skipping them')
    soup = BeautifulSoup(driver.page_source, "lxml")
    sea = soup.find_all('div', class_='x9f619 x78zum5 x1r8uery xdt5ytf x1iyjqo2 xs83m0k x1e558r4 x150jy0e x1iorvi4 xjkvuk6 xnpuxes x291uyu x1uepa24')
    for i in sea:
        try:
            lin = i.find('a', class_='x1i10hfl xjbqb8w x1ejq31n xd10rxx x1sy0etr x17r0tee x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz x1heor9g xkrqix3 x1sur9pj x1s688f x1lku1pv')
            url = 'https://www.facebook.com' + lin['href']
            urls.append({'Name': name, 'url': url})
        except:
            pass
    print(urls)
    return urls


def check_and_get_data_for_iphones(driver, link, name):
    try:
        driver.get(link)

        # Extract Title
        title_xpath = "//span[@class='x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x x14z4hjw x3x7a5m xngnso2 x1qb5hxa x1xlr1w8 xzsf02u']"
        title_elems = WebDriverWait(driver, 20).until(
            ec.presence_of_all_elements_located((By.XPATH, title_xpath))
        )

        if not title_elems:
            print(f"[{name}] ❌ No title elements found.")
            return None

        title_text = title_elems[-1].text.strip().lower()

        def normalize(text):
            return text.lower().replace(" ", "").replace("-", "")

        normalized_title = normalize(title_text)
        normalized_name = normalize(name)

        if normalized_name not in normalized_title:
            print(f"[{name}] Skipped: Title does not match search keywords. ({title_text})")
            return None
        check = check_fb_location(driver)
        if check:
            joined_xpath = "//span[@class='x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x xudqn12 x3x7a5m x6prxxf xvq8zen xo1l8bm xzsf02u x1yc453h']"
            date_jo = WebDriverWait(driver, 10).until(
                ec.presence_of_all_elements_located((By.XPATH, joined_xpath))
            )
            date_joined = int(date_jo[-1].text.strip()[-4:])
            if date_joined > 2022:
                print(f"[{name}] Skipped: date joined does not match. {date_joined}")
                return None
            print(f"[{name}] Title: {title_text}")

            price_xpath = "//span[@class='x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x xudqn12 x676frb x1lkfr7t x1lbecb7 xk50ysn xzsf02u']"
            price_elem = WebDriverWait(driver, 10).until(
                ec.presence_of_element_located((By.XPATH, price_xpath))
            )

            price_raw = price_elem.text.strip()
            price_match = re.search(r'\d+(?:,\d{3})*(?:\.\d{2})?', price_raw)
            if not price_match:
                print(f"[{name}] ❌ Skipping: Could not extract valid price from: {price_raw}")
                return None

            price = float(price_match.group(0).replace(',', ''))
            if '256' in title_text:
                storage = '256GB'
            elif '128' in title_text:
                storage = '128GB'
            elif '512' in title_text:
                storage = '512GB'
            elif '1 tb' in title_text or '1tb' in title_text:
                storage = '1TB'
            else:
                storage = 'unknown'

            if storage == 'unknown':
                print('Checking through description')
                try:
                    desc = driver.find_element(By.XPATH, "//div[@class='xz9dl7a x4uap5 xsag5q8 xkhd6sd x126k92a']").text.strip()
                    if '256' in desc:
                        storage = '256GB'
                    elif '128' in desc:
                        storage = '128GB'
                    elif '512' in desc:
                        storage = '512GB'
                    elif '1 tb' in desc or '1tb' in desc:
                        storage = '1TB'
                    else:
                        storage = '128GB'
                except:
                    pass
            else:
                print('Storage in title')

            print(f"[{name}] Price: £{price}")
            print(f"[{name}] Date Joined: {date_joined}")
            print(f"[{name}] Storage: {storage}")

            return {
                "Link": link,
                "name": name,
                "title": title_text,
                "price": price,
                "storage": storage,
                "date_joined": date_joined,
            }
        else:
            print('Location is not available in the list. Skipping....')
    except TimeoutException:
        print(f"[{name}] ⏰ Timeout while waiting for elements on page: {link}")
        return None
    except Exception as e:
        print(f"[{name}] 🔥 Unexpected error: {e}")
        return None


def get_pro_m4(driver, link, name, music_magpie_price):
    try:
        driver.get(link)
        check = check_fb_location(driver)
        if check:
            title_xpath = "//span[@class='x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x x14z4hjw x3x7a5m xngnso2 x1qb5hxa x1xlr1w8 xzsf02u']"
            title_elems = WebDriverWait(driver, 20).until(
                ec.presence_of_all_elements_located((By.XPATH, title_xpath))
            )

            if not title_elems:
                print(f"[{name}] ❌ No title elements found.")
                return None
            title_text = title_elems[-1].text.strip().lower()

            print(f"[{name}] Title: {title_text}")
            desc = WebDriverWait(driver, 20).until(ec.presence_of_element_located((By.XPATH, "//div[@class='xz9dl7a x4uap5 xsag5q8 xkhd6sd x126k92a']")))
            title_upper = title_text.upper()
            desc_upper = desc.text.strip().upper()

            if all(keyword in title_upper for keyword in ['M4', 'PRO', '24']) or all(
                    keyword in desc_upper for keyword in ['M4', 'PRO', '24']):
                price_xpath = "//span[@class='x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x xudqn12 x676frb x1lkfr7t x1lbecb7 xk50ysn xzsf02u']"
                price_elem = WebDriverWait(driver, 10).until(
                    ec.presence_of_element_located((By.XPATH, price_xpath))
                )

                price_raw = price_elem.text.strip()
                price_match = re.search(r'\d+(?:,\d{3})*(?:\.\d{2})?', price_raw)
                if not price_match:
                    print(f"[{name}] ❌ Skipping: Could not extract valid price from: {price_raw}")
                    return None

                price = float(price_match.group(0).replace(',', ''))

                # Seller Join Date
                joined_xpath = "//span[@class='x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x xudqn12 x3x7a5m x6prxxf xvq8zen xo1l8bm xzsf02u x1yc453h']"
                date_jo = WebDriverWait(driver, 10).until(
                    ec.presence_of_all_elements_located((By.XPATH, joined_xpath))
                )
                date_joined = int(date_jo[-1].text.strip()[-4:])

                print(f"[{name}] Price: £{price}")
                print(f"[{name}] Date Joined: {date_joined}")

                # Return the data as a dictionary
                return {
                    "Link": link,
                    "name": name,
                    "title": title_text,
                    "price": price,
                    "date_joined": date_joined,
                    "meets_criteria": (
                        date_joined <= 2022 and price <= music_magpie_price * 1.25
                    ),
                }
            else:
                print("Listing doesn't fulfills the requirement.")
        else:
            print('Location is not available in the list. Skipping....')
    except TimeoutException:
        print(f"[{name}] ⏰ Timeout while waiting for elements on page: {link}")
        return None
    except Exception as e:
        print(f"[{name}] 🔥 Unexpected error: {e}")
        return None


def get_air_m4(driver, link, name, music_magpie_price):
    try:
        driver.get(link)
        check = check_fb_location(driver)
        if check:
            # Extract Title
            title_xpath = "//span[@class='x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x x14z4hjw x3x7a5m xngnso2 x1qb5hxa x1xlr1w8 xzsf02u']"
            title_elems = WebDriverWait(driver, 20).until(
                ec.presence_of_all_elements_located((By.XPATH, title_xpath))
            )

            if not title_elems:
                print(f"[{name}] ❌ No title elements found.")
                return None
            title_text = title_elems[-1].text.strip().lower()

            print(f"[{name}] Title: {title_text}")
            desc = WebDriverWait(driver, 20).until(
                ec.presence_of_element_located((By.XPATH, "//div[@class='xz9dl7a x4uap5 xsag5q8 xkhd6sd x126k92a']")))
            title_upper = title_text.upper()
            desc_upper = desc.text.strip().upper()

            if all(keyword in title_upper for keyword in ['M4', 'AIR', '16']) or all(
                    keyword in desc_upper for keyword in ['M4', 'AIR', '16']):
                price_xpath = "//span[@class='x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x xudqn12 x676frb x1lkfr7t x1lbecb7 xk50ysn xzsf02u']"
                price_elem = WebDriverWait(driver, 10).until(
                    ec.presence_of_element_located((By.XPATH, price_xpath))
                )

                price_raw = price_elem.text.strip()
                price_match = re.search(r'\d+(?:,\d{3})*(?:\.\d{2})?', price_raw)
                if not price_match:
                    print(f"[{name}] ❌ Skipping: Could not extract valid price from: {price_raw}")
                    return None

                price = float(price_match.group(0).replace(',', ''))

                # Seller Join Date
                joined_xpath = "//span[@class='x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x xudqn12 x3x7a5m x6prxxf xvq8zen xo1l8bm xzsf02u x1yc453h']"
                date_jo = WebDriverWait(driver, 10).until(
                    ec.presence_of_all_elements_located((By.XPATH, joined_xpath))
                )
                date_joined = int(date_jo[-1].text.strip()[-4:])

                print(f"[{name}] Price: £{price}")
                print(f"[{name}] Date Joined: {date_joined}")

                # Return the data as a dictionary
                return {
                    "Link": link,
                    "name": name,
                    "title": title_text,
                    "price": price,
                    "date_joined": date_joined,
                    "meets_criteria": (
                            date_joined <= 2022 and price <= music_magpie_price * 1.25
                    ),
                }
            else:
                print("Listing doesn't fulfills the requirement.")
        else:
            print('Location is not available in the list. Skipping....')
    except TimeoutException:
        print(f"[{name}] ⏰ Timeout while waiting for elements on page: {link}")
        return None
    except Exception as e:
        print(f"[{name}] 🔥 Unexpected error: {e}")
        return None


def get_watch(link, name, music):
    try:
        driver.get(link)
        check = check_fb_location(driver)
        if check:
            # Extract Title
            title_xpath = "//span[@class='x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x x14z4hjw x3x7a5m xngnso2 x1qb5hxa x1xlr1w8 xzsf02u']"
            title_elems = WebDriverWait(driver, 20).until(
                ec.presence_of_all_elements_located((By.XPATH, title_xpath))
            )

            if not title_elems:
                print(f"[{name}] ❌ No title elements found.")
                return None
            title_text = title_elems[-1].text.strip().lower()

            print(f"[{name}] Title: {title_text}")
            desc = WebDriverWait(driver, 20).until(
                ec.presence_of_element_located((By.XPATH, "//div[@class='xz9dl7a x4uap5 xsag5q8 xkhd6sd x126k92a']")))
            title_upper = title_text.upper()
            desc_upper = desc.text.strip().upper()

            if all(keyword in title_upper for keyword in ['ULTRA 2', 'WATCH', 'APPLE']) or all(
                    keyword in desc_upper for keyword in ['ULTRA 2', 'WATCH', 'APPLE']):
                price_xpath = "//span[@class='x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x xudqn12 x676frb x1lkfr7t x1lbecb7 xk50ysn xzsf02u']"
                price_elem = WebDriverWait(driver, 10).until(
                    ec.presence_of_element_located((By.XPATH, price_xpath))
                )

                price_raw = price_elem.text.strip()
                price_match = re.search(r'\d+(?:,\d{3})*(?:\.\d{2})?', price_raw)
                if not price_match:
                    print(f"[{name}] ❌ Skipping: Could not extract valid price from: {price_raw}")
                    return None

                price = float(price_match.group(0).replace(',', ''))

                # Seller Join Date
                joined_xpath = "//span[@class='x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x xudqn12 x3x7a5m x6prxxf xvq8zen xo1l8bm xzsf02u x1yc453h']"
                date_jo = WebDriverWait(driver, 10).until(
                    ec.presence_of_all_elements_located((By.XPATH, joined_xpath))
                )
                date_joined = int(date_jo[-1].text.strip()[-4:])

                print(f"[{name}] Price: £{price}")
                print(f"[{name}] Date Joined: {date_joined}")

                # Return the data as a dictionary
                return {
                    "Link": link,
                    "name": name,
                    "title": title_text,
                    "price": price,
                    "date_joined": date_joined,
                    "meets_criteria": (
                            date_joined <= 2022 and price <= music * 1.25
                    ),
                }
            else:
                print("Listing doesn't fulfills the requirement.")
        else:
            print('Location is not available in the list. Skipping....')
    except TimeoutException:
        print(f"[{name}] ⏰ Timeout while waiting for elements on page: {link}")
        return None
    except Exception as e:
        print(f"[{name}] 🔥 Unexpected error: {e}")
        return None


def get_music_pie_i_phones(driver, na, storage):
    driver.get('https://www.musicmagpie.co.uk/start-selling')
    inp = WebDriverWait(driver, 120).until(ec.presence_of_element_located((By.XPATH, "//input[@id='productSearch']")))
    inp.send_keys(f"{na} {storage}")
    results = WebDriverWait(driver, 15).until(ec.presence_of_all_elements_located((By.XPATH, "//a[@class='autocomplete-list-link']")))
    for i in results:
        title = i.get_attribute('title')
        if storage.upper() in title.upper():
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", i)
            driver.execute_script("arguments[0].click(true);", i)
            print('Clicked successfully!')
            break
    price = WebDriverWait(driver, 20).until(ec.presence_of_element_located((By.XPATH, "//span[@class='productPrice']")))
    return price.text[1:]


def get_music_pie_air(driver, na, ram):
    driver.get('https://www.musicmagpie.co.uk/start-selling')
    inp = WebDriverWait(driver, 20).until(ec.presence_of_element_located((By.XPATH, "//input[@id='productSearch']")))
    inp.send_keys(f"{na} {ram}GB")
    results = WebDriverWait(driver, 15).until(ec.presence_of_all_elements_located((By.XPATH, "//a[@class='autocomplete-list-link']")))
    for i in results:
        title = i.get_attribute('title')
        if ram.upper() in title.upper() and "M4" in title.upper():
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", i)
            driver.execute_script("arguments[0].click(true);", i)
            print('Clicked successfully!')
            break
    price = WebDriverWait(driver, 20).until(ec.presence_of_element_located((By.XPATH, "//span[@class='productPrice']")))
    return price.text[1:]


def get_music_pie_pro(driver, na, ram):
    driver.get('https://www.musicmagpie.co.uk/start-selling')
    inp = WebDriverWait(driver, 20).until(ec.presence_of_element_located((By.XPATH, "//input[@id='productSearch']")))
    inp.send_keys(f"{na} {ram}GB")
    results = WebDriverWait(driver, 15).until(
        ec.presence_of_all_elements_located((By.XPATH, "//a[@class='autocomplete-list-link']")))
    for i in results:
        title = i.get_attribute('title')
        if ram.upper() in title.upper() and "M4" in title.upper():
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", i)
            driver.execute_script("arguments[0].click(true);", i)
            print('Clicked successfully!')
            break
    price = WebDriverWait(driver, 20).until(ec.presence_of_element_located((By.XPATH, "//span[@class='productPrice']")))
    return price.text[1:]


def get_music_watch(dr):
    dr.get('https://www.musicmagpie.co.uk/product-details?barcode=i000000048995')
    price = WebDriverWait(driver, 20).until(ec.presence_of_element_located((By.XPATH, "//span[@class='productPrice']")))
    return price.text[1:]


def main(fb_driver, mm_driver, fb_ads):
    matched_ads = []
    seen_links = set()

    # Load previously alerted links
    alerted_file = "matched_links.txt"
    if os.path.exists(alerted_file):
        with open(alerted_file, "r") as file:
            alerted_links = set(line.strip() for line in file)
    else:
        alerted_links = set()

    for ad in fb_ads:
        raw_link = ad["link"]
        link = normalize_fb_link(raw_link)
        name = ad["name"]

        if link in seen_links or link in alerted_links:
            continue
        seen_links.add(link)

        print(f"\n📄 Checking: {name} → {link}")

        # Get FB ad data
        fb_data = check_and_get_data_for_iphones(fb_driver, link, name)
        if fb_data is None:
            print("⚠️ Skipping: No FB data found.")
            continue

        fb_price = fb_data['price']
        storage = fb_data['storage']
        date_joined = fb_data['date_joined']

        print(f"📊 FB Price: £{fb_price} | Storage: {storage} | Joined: {date_joined}")

        if fb_price < 200:
            print("🚫 Skipped: FB price too low.")
            continue
        if date_joined > 2022:
            print("🚫 Skipped: Seller too new.")
            continue

        try:
            mm_price_text = get_music_pie_i_phones(mm_driver, name, storage)
            mm_price_text = mm_price_text.replace(',', '').strip()

            if not re.match(r'^\d+(\.\d+)?$', mm_price_text):
                raise ValueError(f"Invalid price format: '{mm_price_text}'")

            mm_price = float(mm_price_text)

        except Exception as e:
            print(f"❌ Magpie lookup failed for {name} {storage}: {e}")
            continue

        print(f"🎯 Magpie Price: £{mm_price}")
        if fb_price <= mm_price * 1.25:
            mess = f"✅ Matched: FB £{fb_price} ≤ 25% of Music Mag pie £{mm_price}. Link is {link}"
            matched_ads.append(link)
            send_telegram_alert(mess)
            # Write to record file to avoid future duplicates
            try:
                with open(alerted_file, "a") as file:
                    file.write(link + "\n")
            except Exception as e:
                print(f"⚠️ Failed to write to log file: {e}")
        else:
            print(f"❌ Overpriced: FB £{fb_price} > 125% of MM £{mm_price}")

    if matched_ads:
        print("\n✅✅ Final Matches:")
        for match in matched_ads:
            print(f"🔗 {match}")
    else:
        print("\n🚫 No iPhones matched your criteria.")


def run(driver):
    # fb_driver = set_up_driver()
    # mm_driver = set_up_driver()
    iphones = ['IPhone 15 pro max',
               'IPhone 15',
               'Iphone 15 plus',
               'IPhone 14 pro max',
               'IPhone 14 plus',
               'IPhone 14',
               'IPhone 13 pro max',
               ]
    fb_ads = []

    for model in iphones:
        urls = market_place(driver, model)
        for ad in urls:
            fb_ads.append({"name": model, "link": ad['url']})

    main(driver, driver, fb_ads)


def main1(fb_driver, mm_driver, fb_ads):
    matched_ads = []
    seen_links = set()

    alerted_file = "matched_links.txt"
    try:
        with open(alerted_file, "r") as file:
            alerted_links = set(line.strip() for line in file if line.strip())
    except FileNotFoundError:
        alerted_links = set()

    mm_price = 0
    try:
        mm_price_text = get_music_pie_pro(mm_driver, "Apple Macbook Pro M4", '24')
        mm_price_text = mm_price_text.replace(',', '').strip()

        if not re.match(r'^\d+(\.\d+)?$', mm_price_text):
            raise ValueError(f"Invalid price format: '{mm_price_text}'")

        mm_price = float(mm_price_text)

    except Exception as e:
        print(f"❌ Magpie lookup failed: {e}")
        return

    for ad in fb_ads:
        raw_link = ad["link"]
        link = normalize_fb_link(raw_link)
        name = ad["name"]

        if link in seen_links or link in alerted_links:
            continue
        seen_links.add(link)

        fb_data = get_pro_m4(fb_driver, link, name, None)
        if not fb_data:
            continue

        if not fb_data["meets_criteria"]:
            print(f"❌ Overpriced or seller too new: {name} | FB: £{fb_data['price']}")
            continue

        if fb_data["meets_criteria"]:
            matched_ads.append(link)
            msg = f"✅ Matched: {name}\nFB: £{fb_data['price']} | MusicMagPie: £{mm_price}\n🔗 {link}"
            print(msg)
            send_telegram_alert(msg)

            with open(alerted_file, "a") as file:
                file.write(link + "\n")
        else:
            print(f"❌ Overpriced or seller too new: {name} | FB: £{fb_data['price']} | MM: £{mm_price}")

    if not matched_ads:
        print("🚫 No M4 Pro 24GB matched with criteria.")


def run1(driver):
    # driver = set_up_driver()
    fb_ads = []

    queries = ['Apple Macbook Pro M4']

    for query in queries:
        listings = market_place(driver, query)
        for listing in listings:
            fb_ads.append({
                "link": listing['url'],
                "name": query
            })

    main1(driver, driver, fb_ads)


def main2(fb_driver, mm_driver, fb_ads):
    matched_ads = []
    seen_links = set()
    mm_price = 800

    alerted_file = "matched_links.txt"
    if os.path.exists(alerted_file):
        with open(alerted_file, "r") as file:
            alerted_links = set(line.strip() for line in file)
    else:
        alerted_links = set()

    try:
        mm_price_text = get_music_pie_air(mm_driver, "Apple Macbook Air M4", '16')

        if not re.match(r'^\d+(\.\d+)?$', mm_price_text):
            raise ValueError(f"Invalid price format: '{mm_price_text}'")

        mm_price = float(mm_price_text)

    except Exception as e:
        print(f"❌ Magpie lookup failed: {e}")

    for ad in fb_ads:
        raw_link = ad["link"]
        link = normalize_fb_link(raw_link)
        name = ad["name"]

        if link in seen_links or link in alerted_links:
            continue
        seen_links.add(link)

        fb_data = get_air_m4(fb_driver, link, name, mm_price)
        if not fb_data:
            continue

        if fb_data["meets_criteria"]:
            matched_ads.append(link)
            msg = f"✅ Matched: {name}\nFB: £{fb_data['price']} | MusicMagPie: £{mm_price}\n🔗 {link}"
            print(msg)
            send_telegram_alert(msg)
            try:
                with open(alerted_file, "a") as file:
                    file.write(link + "\n")
            except Exception as e:
                print(f"⚠️ Failed to write to log file: {e}")
        else:
            print(f"❌ Overpriced or seller too new: {name} | FB: £{fb_data['price']} | MM: £{mm_price}")
            continue

    if not matched_ads:
        print("🚫 No MacBook Air M4 16GB matched the criteria.")


def run2(driver):
    # driver = set_up_driver()
    fb_ads = []

    queries = ['Apple MacBook Air M4']

    for query in queries:
        listings = market_place(driver, query)
        for listing in listings:
            fb_ads.append({
                "link": listing['url'],
                "name": query
            })

    main2(driver, driver, fb_ads)


def main_watch(fb_driver, mm_driver, fb_ads):
    matched_ads = []
    seen_links = set()

    alerted_file = "matched_links.txt"
    if os.path.exists(alerted_file):
        with open(alerted_file, "r") as file:
            alerted_links = set(line.strip() for line in file)
    else:
        alerted_links = set()

    try:
        mm_price_text = get_music_watch(mm_driver)
        mm_price_text = mm_price_text.replace(',', '').strip()

        if not re.match(r'^\d+(\.\d+)?$', mm_price_text):
            raise ValueError(f"Invalid price format: '{mm_price_text}'")

        mm_price = float(mm_price_text)
    except Exception as e:
        print(f"❌ Magpie lookup failed: {e}")
        return

    for ad in fb_ads:
        raw_link = ad["link"]
        link = normalize_fb_link(raw_link)
        name = ad["name"]

        if link in seen_links or link in alerted_links:
            continue
        seen_links.add(link)

        fb_data = get_watch(link, name, mm_price)
        if not fb_data:
            continue

        if fb_data["meets_criteria"]:
            matched_ads.append(link)
            msg = (
                f"✅ Matched: {name}\n"
                f"FB: £{fb_data['price']} | MusicMagPie: £{mm_price}\n"
                f"🔗 {link}"
            )
            print(msg)
            send_telegram_alert(msg)
            try:
                with open(alerted_file, "a") as file:
                    file.write(link + "\n")
            except Exception as e:
                print(f"⚠️ Failed to write to log file: {e}")
        else:
            print(
                f"❌ Overpriced or seller too new: {name} | "
                f"FB: £{fb_data['price']} | MM: £{mm_price}"
            )

    if not matched_ads:
        print("🚫 No Apple Watch Ultra 2 matched the criteria.")


def run3(driver):
    fb_ads = []
    queries = ['Apple Watch Ultra 2']

    for query in queries:
        listings = market_place(driver, query)
        for listing in listings:
            fb_ads.append({
                "link": listing['url'],
                "name": query
            })

    main_watch(driver, driver, fb_ads)


if __name__ == "__main__":
    i = 0
    while True:
        driver = None
        try:
            driver = set_up_driver()
            print(f'Running the code {i + 1} time. Then will sleep for 3 hours!')
            run(driver)
            run1(driver)
            run2(driver)
            run3(driver)
        except Exception as e:
            print(f"Error on run {i + 1}: {e}")
            traceback.print_exc()
        finally:
            if driver:
                driver.quit()
            i += 1
            time.sleep(10800)


