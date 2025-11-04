

import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import csv
csv_file = open("youtube_video_data.csv", "w", newline="", encoding="utf-8")
csv_writer = csv.writer(csv_file)
csv_writer.writerow(["Video URL", "Views", "Likes", "Comments", "Description"])

# ===============================
#  LIST OF VIDEO URLS
# ===============================
VIDEO_URLS = [
    "https://www.youtube.com/watch?v=jfWSQyRI8dQ",
    "https://www.youtube.com/watch?v=FpO6Ziifvs0",
    "https://www.youtube.com/watch?v=pUi_CZusepI",
    "https://www.youtube.com/watch?v=mhBcqBuXjT0",
    "https://www.youtube.com/watch?v=JQL3q9o7Lz0"
]


options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
# You can uncomment below to run in headless mode
# options.add_argument("--headless=new")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
# ===============================
#  FUNCTION: FETCH VIDEO DETAILS
# ===============================
def process_video(video_url):
    print("\n" + "=" * 80)
    print(f"🎥 Processing video: {video_url}")
    print("=" * 80)

    
    driver.get(video_url)
    time.sleep(10)
    wait = WebDriverWait(driver, 10)

    html = driver.page_source

    # --- Extract title ---
    title_match = re.search(r'<title>(.*?)</title>', html)
    title = title_match.group(1).strip() if title_match else "N/A"

    # --- Extract subscribers ---
    subs_match = re.search(r'<yt-formatted-string[^>]*id="owner-sub-count"[^>]*>(.*?)</yt-formatted-string>', html)
    subscribers = subs_match.group(1).strip() if subs_match else "N/A"

    # --- Extract likes ---
    likes_match = re.search(
        r'<div class="yt-spec-button-shape-next__button-text-content">\s*([\d.,KM]+)\s*</div>', html)
    likes = likes_match.group(1).strip() if likes_match else "N/A"

    # --- Extract views ---
    try:
        element = driver.find_element(By.XPATH, '//*[@id="info"]/span[1]')
        views_text = element.text.strip()
    except Exception:
        views_text = "N/A"
    #print(f"Raw text from XPath: {views_text}")

    # --- Extract comment count ---
    comments_xpath = "//div[@id='title']//*[@id='count']//span[1]"
    driver.execute_script("window.scrollBy(0, arguments[0]);", 600)
    try:
        v_comm_cnt = wait.until(EC.visibility_of_element_located((By.XPATH, comments_xpath))).text
    except Exception:
        try:
            v_comm_cnt = driver.find_element(By.XPATH, comments_xpath).text
        except Exception:
            v_comm_cnt = "N/A"

    # --- Extract description ---
    description = None
    try:
        # Wait for description block
        desc_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "description-inline-expander"))
        )
        # Try to click "Show more"
        try:
            show_more_button = driver.find_element(By.ID, "expand")
            show_more_button.click()
            time.sleep(1)
        except Exception:
            pass
        description = desc_element.text.strip()
    except Exception as e:
        print(f"Error extracting description: {e}")
        description = None

    # --- Print results ---
    print(f"Title: {title}")
    print(f"Subscribers: {subscribers}")
    print(f"Likes: {likes}")
    print(f"Views: {views_text}")
    print(f"Comments: {v_comm_cnt}")
    if description:
        print("Video Description:")
        print(description)
    else:
        print("Could not retrieve video description.")

    csv_writer.writerow([
        video_url,
        views_text,
        likes,
        v_comm_cnt,
        description if description else "N/A"
    ])



# ===============================
#  MAIN EXECUTION LOOP
# ===============================
for url in VIDEO_URLS:
    process_video(url)
driver.quit()
print("\n✅ Completed scraping all provided YouTube URLs.")
csv_file.close()
