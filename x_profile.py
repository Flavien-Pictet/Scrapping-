import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
import csv
import re
import pandas as pd
import os

driver = webdriver.Chrome()

def random_sleep(min_seconds, max_seconds):
    time.sleep(random.uniform(min_seconds, max_seconds))

def extract_keyword(url):
    match = re.search(r'q=([^&]+)', url)
    if match:
        keyword = match.group(1).replace('%20', '').lower()
        return keyword
    else:
        return 'output'


# Add your own Twitter research link in the "search_url" variable.
search_url = 'https://x.com/search?q=MyProtein&src=typed_query&f=user'
keyword = extract_keyword(search_url)

driver.get('https://x.com/login')

# Add your own cookie
cookie = {
    'name': 'auth_token',
    'value': os.environ['X_AUTH_TOKEN'],
    'domain': '.x.com',  
    'path': '/',
    'httpOnly': True,
    'secure': True
}

driver.add_cookie(cookie)
random_sleep(2, 4)

driver.get(search_url)
random_sleep(3, 5)

def get_usernames():
    usernames = []
    try:
        elements = driver.find_elements(By.XPATH, '//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/section/div/div/div/div/div/button/div/div[2]/div[1]/div[1]/div/div[2]/div/a/div/div/span')
        for elem in elements:
            usernames.append(elem.text)
    except Exception as e:
        print(f"Error getting usernames: {e}")
    return usernames

def scroll_down():
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    random_sleep(2, 4)
    
all_usernames = set()
try:
    for _ in range(100): 
        new_usernames = set(get_usernames())
        all_usernames.update(new_usernames)
        scroll_down()
        print(f"Scraped {len(all_usernames)} usernames so far.")
        if len(new_usernames) == 0: 
            break
except Exception as e:
    print(f"Error during scraping: {e}")


csv_filename = f'{keyword}.csv'
try:
    with open(csv_filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["username"])
        for username in all_usernames:
            writer.writerow([username])
    print(f"Usernames saved to {csv_filename}")
except Exception as e:
    print(f"Error writing to CSV: {e}")

driver.quit()

input_csv_path = csv_filename
output_csv_path = csv_filename
df = pd.read_csv(input_csv_path)

df['profile_url'] = df['username'].apply(lambda x: f"https://x.com/{x.lstrip('@').lower()}")
df_cleaned = df['profile_url'].drop_duplicates()

df_cleaned.to_csv(output_csv_path, index=False, header=False)
print(f"Cleaned data saved to {output_csv_path}")