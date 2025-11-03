import time
import os
import requests
import math
import re
import numpy as np
import csv
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

listings_per_page = 18  # Airbnb shows 18 listings per page by default

# Define the region boundaries and raster pitch
ne_lat = -8.43035852742501
ne_lng = 115.294281018947
sw_lat = -8.537853723685433
sw_lng = 115.22152509345563

lat_pitch = 0.00907288127
lng_pitch = 0.00953707562

# Define the start date and other URL parameters
start_date = '2025-12-01'
end_date = '2026-02-01'
monthly_length = 3
zoom_level = 21.7895

# Setup the Chrome driver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.maximize_window()

# Function to download and save the image
def download_image(image_url, listing_id):
    try:
        if not os.path.exists("Airbnb"):
            os.makedirs("Airbnb")
        img_data = requests.get(image_url, verify=False).content
        image_path = os.path.join("Airbnb", f"Property{listing_id}.jpeg")
        with open(image_path, 'wb') as img_file:
            img_file.write(img_data)
        print(f"Image for Property {listing_id} saved successfully.")
        return image_path
    except Exception as e:
        print(f"Error downloading image for Property {listing_id}: {e}")
        return "N/A"

# Initialize an HTML structure (will be finalized later)
html_content = """
<html>
<head>
    <title>Airbnb Listings</title>
    <style>
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            border: 1px solid black;
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
        }
        img {
            width: 100px;
            height: auto;
        }
    </style>
</head>
<body>
    <h1>Airbnb Listings</h1>
    <table>
        <thead>
            <tr>
                <th>Property Name</th>
                <th>Price</th>
                <th>Rating</th>
                <th>Reviews</th>
                <th>URL</th>
                <th>Listing ID</th>
                <th>Image Path</th>
                <th>Image URL</th>
            </tr>
        </thead>
        <tbody>
"""

html_file = open("Airbnb_listings.html", "w", encoding="utf-8")
html_file.write(html_content)

# Initialize CSV file for raw data
csv_file_path = "Airbnb_listings_raw.csv"
csv_columns = ["Property Name", "Price", "Rating", "Reviews", "URL", "Listing ID", "Image Path", "Image URL"]

with open(csv_file_path, "w", newline="", encoding="utf-8") as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(csv_columns)

# Function to extract listings
def extract_listings():
    listings = driver.find_elements(By.XPATH, "//div[@itemprop='itemListElement']")
    print(f"Found {len(listings)} listings.\n")

    for listing in listings:
        try:
            name = listing.find_element(By.XPATH, ".//div[@data-testid='listing-card-title']").text
        except:
            name = "N/A"

        try:
            span_elements = listing.find_elements(By.XPATH, ".//span[contains(text(), 'Rp')]")
            price = "N/A"
            for span in span_elements:
                text = span.text.strip()
                if "originally" in text.lower() or "for" in text.lower():
                    continue
                if text.startswith('Rp'):
                    price = text
                    break
        except:
            price = "N/A"

        try:
            rating_element = listing.find_element(By.XPATH, ".//span[contains(text(), 'out of 5 average rating')]")
            rating_text = rating_element.text.strip()
            rating = rating_text.split(" out of ")[0].strip()
            reviews = rating_text.split("reviews")[0].split(",")[-1].strip()
        except:
            rating = "N/A"
            reviews = "N/A"

        try:
            url_element = listing.find_element(By.TAG_NAME, 'a')
            full_url = url_element.get_attribute('href')
            base_url = full_url.split('?')[0]
            listing_id = base_url.split('/')[-1]
        except:
            base_url = "N/A"
            listing_id = "N/A"
            
        try:
            img_element = listing.find_element(By.XPATH, ".//img[@aria-hidden='true']")
            image_url = img_element.get_attribute("src")
            image_path = download_image(image_url, listing_id)
        except Exception as e:
            image_url = "N/A"
            image_path = "N/A"
            print(f"Image not found for Property {listing_id}: {e}")

        # Write to HTML file
        html_file.write(f"""
        <tr>
            <td>{name}</td>
            <td>{price}</td>
            <td>{rating}</td>
            <td>{reviews}</td>
            <td><a href="{base_url}" target="_blank">{base_url}</a></td>
            <td>{listing_id}</td>
            <td><img src="{image_path}" alt="Image of {name}"></td>
            <td><a href="{image_url}" target="_blank">Image Link</a></td>
        </tr>
        """)

        # Write to CSV
        with open(csv_file_path, "a", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow([name, price, rating, reviews, base_url, listing_id, image_path, image_url])

        print(f"Property Name: {name}")
        print(f"Price: {price}")
        print(f"Rating: {rating}")
        print(f"Reviews: {reviews}")
        print(f"URL: {base_url}")
        print(f"Listing ID: {listing_id}")
        print("-" * 50)


# --- NEW FUNCTION: Recursive grid handler ---
def process_grid(sw_lat_new, sw_lng_new, ne_lat_new, ne_lng_new, lat_pitch, lng_pitch):
    url = f"https://www.airbnb.com/s/Bali/homes?flexible_trip_lengths%5B%5D=one_week&monthly_start_date={start_date}&monthly_length={monthly_length}&monthly_end_date={end_date}&ne_lat={ne_lat_new}&ne_lng={ne_lng_new}&sw_lat={sw_lat_new}&sw_lng={sw_lng_new}&zoom={zoom_level}&zoom_level={zoom_level}"
    print(f"Navigating to URL: {url}")
    driver.get(url)
    time.sleep(5)

    html = driver.page_source
    match = re.search(r'(\d+)\s+home[s]?\s+within map area', html, re.IGNORECASE)
    if match:
        count = int(match.group(1))
        print(f"✅ Found {count} home(s) within map area.")
    else:
        print("❌ Could not find home count in page source.")
        return

    # If too many listings, subdivide further
    if count > 270:
        print("⚠️ Too many listings, subdividing grid...")
        new_lat_pitch = lat_pitch / 2
        new_lng_pitch = lng_pitch / 2

        mid_lat = (sw_lat_new + ne_lat_new) / 2
        mid_lng = (sw_lng_new + ne_lng_new) / 2

        # Subdivide into 4 smaller cells
        sub_cells = [
            (sw_lat_new, sw_lng_new, mid_lat, mid_lng),
            (sw_lat_new, mid_lng, mid_lat, ne_lng_new),
            (mid_lat, sw_lng_new, ne_lat_new, mid_lng),
            (mid_lat, mid_lng, ne_lat_new, ne_lng_new)
        ]

        for sub in sub_cells:
            process_grid(sub[0], sub[1], sub[2], sub[3], new_lat_pitch, new_lng_pitch)
        return

    # If acceptable count, extract listings
    if count == 0:
        return

    num_pages = math.ceil(count / listings_per_page)
    current_page = 1
    extract_listings()

    while current_page < num_pages:
        try:
            next_button = driver.find_element(By.XPATH, "//a[@aria-label='Next']")
            next_url = next_button.get_attribute("href")
            if next_url:
                driver.get(next_url)
                time.sleep(5)
                current_page += 1
                print(f"Navigating to page {current_page}/{num_pages}: {next_url}")
                extract_listings()
            else:
                break
        except Exception as e:
            print("Reached the last page or error occurred. Exiting this URL.")
            break


# --- MAIN LOOP WITH GRACEFUL EXIT ---
try:
    latitudes = np.arange(sw_lat, ne_lat, lat_pitch)
    longitudes = np.arange(sw_lng, ne_lng, lng_pitch)

    for lat in latitudes:
        for lng in longitudes:
            sw_lat_new = lat
            sw_lng_new = lng
            ne_lat_new = lat + lat_pitch
            ne_lng_new = lng + lng_pitch
            process_grid(sw_lat_new, sw_lng_new, ne_lat_new, ne_lng_new, lat_pitch, lng_pitch)

except KeyboardInterrupt:
    print("\n🛑 Graceful shutdown requested by user. Exiting...")
finally:
    driver.quit()
    html_file.write("""
            </tbody>
        </table>
    </body>
    </html>
    """)
    html_file.close()
    print("✅ Driver closed and HTML file finalized.")

# --- Deduplicate and generate final HTML ---
print("\n🔍 Removing duplicates and generating final HTML...")

df = pd.read_csv(csv_file_path)
df.drop_duplicates(subset=["Listing ID"], keep="first", inplace=True)
df.to_csv("Airbnb_listings_deduped.csv", index=False)

with open("Airbnb_listings_final.html", "w", encoding="utf-8") as f:
    f.write("""
    <html>
    <head>
        <title>Airbnb Listings</title>
        <style>
            table { width: 100%; border-collapse: collapse; }
            th, td { border: 1px solid black; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            img { width: 100px; height: auto; }
        </style>
    </head>
    <body>
        <h1>Airbnb Listings (Deduplicated)</h1>
        <table>
            <thead>
                <tr>
                    <th>Property Name</th>
                    <th>Price</th>
                    <th>Rating</th>
                    <th>Reviews</th>
                    <th>URL</th>
                    <th>Listing ID</th>
                    <th>Image Path</th>
                    <th>Image URL</th>
                </tr>
            </thead>
            <tbody>
    """)

    for _, row in df.iterrows():
        f.write(f"""
        <tr>
            <td>{row['Property Name']}</td>
            <td>{row['Price']}</td>
            <td>{row['Rating']}</td>
            <td>{row['Reviews']}</td>
            <td><a href="{row['URL']}" target="_blank">{row['URL']}</a></td>
            <td>{row['Listing ID']}</td>
            <td><img src="{row['Image Path']}" alt="Image of {row['Property Name']}"></td>
            <td><a href="{row['Image URL']}" target="_blank">Image Link</a></td>
        </tr>
        """)

    f.write("""
            </tbody>
        </table>
    </body>
    </html>
    """)

print("✅ Deduplication complete. Final HTML saved as 'Airbnb_listings_final.html'.")
