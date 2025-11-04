# -*- coding: utf-8 -*-
"""
Created on Fri Aug 29 10:42:07 2025

@author: wb641752
"""


import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Configuration
CHANNEL_VIDEOS_URL = "https://www.youtube.com/channel/UC3J4Q1grz46bdJ7NJLd4DGw/videos"
SCROLL_PAUSE_TIME = 2
MAX_SCROLLS = 3000  # Adjust to load more videos

# Set up Chrome options
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")

# Initialize driver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

try:
    driver.get(CHANNEL_VIDEOS_URL)
    time.sleep(5)  # Wait for initial content to load

    last_height = driver.execute_script("return document.documentElement.scrollHeight")

    for i in range(MAX_SCROLLS):
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
        time.sleep(SCROLL_PAUSE_TIME)

        # Wait for new video elements to appear
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, '//a[contains(@href, "/watch?v=")]'))
        )

        new_height = driver.execute_script("return document.documentElement.scrollHeight")
        if new_height == last_height:
            print(f"Reached end of page after {i+1} scrolls.")
            break
        last_height = new_height
        print(f"Scrolled {i + 1} times...")

    # After scrolling, collect all video links
    video_links = driver.find_elements(By.XPATH, '//a[contains(@href, "/watch?v=")]')
    video_urls = []

    for link in video_links:
        href = link.get_attribute("href")
        if href and "/watch?v=" in href and href not in video_urls:
            video_urls.append(href)

    print(f"\nFound {len(video_urls)} video URLs.\n")

    for url in video_urls:
        print(url)

    # Optional: Save to file
    with open("veritasium_video_urls.txt", "w", encoding="utf-8") as f:
        for url in video_urls:
            f.write(url + "\n")

finally:
    driver.quit()
