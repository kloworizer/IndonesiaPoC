import re
import requests
import pandas as pd
import os
import time
import signal
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


# ---------- CONFIG ----------
INPUT_CSV = "Airbnb_listings_deduped.csv"
WORKING_CSV = "Airbnb_listings_augmented.csv"
FINAL_HTML = "Airbnb_listings_final_augmented.html"
DOWNLOAD_FOLDER = "images"
SAVE_INTERVAL = 10        # Save every N listings
MAX_RETRIES = 3           # Retries per listing
RETRY_WAIT = 3            # Seconds between retries

# ---------- GLOBALS ----------
driver = None
stop_requested = False


# ---------- SIGNAL HANDLER ----------
def handle_exit_signal(sig, frame):
    global stop_requested
    print("\n🛑 Graceful shutdown requested... finishing current task.")
    stop_requested = True


signal.signal(signal.SIGINT, handle_exit_signal)
signal.signal(signal.SIGTERM, handle_exit_signal)


# ---------- SAFE UTILS ----------
def safe_str(val):
    """Safely convert to string for HTML/CSV output."""
    try:
        if val is None or (isinstance(val, float) and pd.isna(val)):
            return ""
        return str(val).strip()
    except Exception:
        return ""


# ---------- DATA EXTRACTION ----------
def get_listing_data(listing_url, property_id, download_folder=DOWNLOAD_FOLDER):
    """
    Extract latitude, longitude, host duration, and host image.
    Retries a few times if page load fails.
    """
    data = {"lat": "", "lng": "", "host_duration": "", "host_image_path": ""}
    attempt = 0

    while attempt < MAX_RETRIES:
        try:
            driver.get(listing_url)
            time.sleep(3)

            html = driver.page_source
            if not html or "html" not in html.lower():
                attempt += 1
                print(f"⚠️ Incomplete page for {property_id}. Retrying ({attempt}/{MAX_RETRIES})...")
                time.sleep(RETRY_WAIT)
                continue

            # Extract coordinates
            lat_match = re.search(r'"lat":([\-0-9.]+)', html)
            lng_match = re.search(r'"lng":([\-0-9.]+)', html)
            if lat_match and lng_match:
                data["lat"] = safe_str(lat_match.group(1))
                data["lng"] = safe_str(lng_match.group(1))

            # Extract host duration
            hosting_match = re.search(r'([0-9]+)\s+(year|month)s?\s+hosting', html)
            if hosting_match:
                data["host_duration"] = safe_str(hosting_match.group(0))

            # Extract host image
            host_image_match = re.search(
                r'https://a0\.muscache\.com/im/pictures/user/[A-Za-z0-9\-/]+?\.(?:jpe?g)',
                html
            )
            if host_image_match:
                host_image_url = safe_str(host_image_match.group(0))
                os.makedirs(download_folder, exist_ok=True)
                local_image_path = os.path.join(download_folder, f"Host{property_id}.jpeg")

                try:
                    img_data = requests.get(host_image_url, verify=False, timeout=10).content
                    with open(local_image_path, "wb") as f:
                        f.write(img_data)
                    data["host_image_path"] = local_image_path
                    print(f"✅ Host image saved for {property_id}")
                except Exception as e:
                    print(f"⚠️ Could not download host image for {property_id}: {e}")

            return data

        except Exception as e:
            attempt += 1
            print(f"⚠️ Attempt {attempt}/{MAX_RETRIES} failed for {property_id}: {e}")
            time.sleep(RETRY_WAIT)

    print(f"❌ Failed to fetch listing {property_id} after {MAX_RETRIES} retries.")
    return data


# ---------- FINAL HTML BUILDER ----------
def generate_html_from_csv(csv_path, output_html="Airbnb_listings_final_augmented.html"):
    """Generate final HTML from Airbnb_listings_augmented.csv."""
    df = pd.read_csv(csv_path)

    html_head = f"""
    <html>
    <head>
        <title>Airbnb Listings - Augmented</title>
        <style>
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ border: 1px solid #ccc; padding: 6px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            img {{ width: 100px; height: auto; }}
            .missing {{ background-color: #ffe0e0; }}
            a.maplink {{ color: white; background-color: green; padding: 4px 8px; border-radius: 4px; text-decoration: none; }}
        </style>
    </head>
    <body>
        <h1>Airbnb Listings (Final Augmented Data)</h1>
        <p>Total Listings: {len(df)}</p>
        <table>
            <thead>
                <tr>
                    <th>Property Name</th>
                    <th>Price</th>
                    <th>Rating</th>
                    <th>Reviews</th>
                    <th>URL</th>
                    <th>Listing ID</th>
                    <th>Image</th>
                    <th>Lens Link</th>
                    <th>Latitude</th>
                    <th>Longitude</th>
                    <th>Map</th>
                    <th>Host Duration</th>
                    <th>Host Image</th>
                </tr>
            </thead>
            <tbody>
    """

    def safe(val):
        return "" if pd.isna(val) else str(val).strip()

    with open(output_html, "w", encoding="utf-8") as f:
        f.write(html_head)

        for _, row in df.iterrows():
            lat = safe(row["Latitude"])
            lng = safe(row["Longitude"])
            missing_class = 'class="missing"' if not lat or not lng else ""

            f.write(f"""
            <tr {missing_class}>
                <td>{safe(row["Property Name"])}</td>
                <td>{safe(row["Price"])}</td>
                <td>{safe(row["Rating"])}</td>
                <td>{safe(row["Reviews"])}</td>
                <td><a href="{safe(row["URL"])}" target="_blank">{safe(row["URL"])}</a></td>
                <td>{safe(row["Listing ID"])}</td>
                <td><img src="{safe(row["Image Path"])}" alt="Property Image"></td>
                <td><a href="{safe(row["Lens Link"])}" target="_blank">Find via Lens</a></td>
                <td>{lat}</td>
                <td>{lng}</td>
                <td><a href="{safe(row["Google Maps Link"])}" target="_blank" class="maplink">View Map</a></td>
                <td>{safe(row["Host Duration"])}</td>
                <td>{'<img src="'+safe(row["Host Image Path"])+'" width="100">' if safe(row["Host Image Path"]) else ''}</td>
            </tr>
            """)

        f.write("""
            </tbody>
        </table>
    </body>
    </html>
    """)

    print(f"✅ Final HTML generated successfully: {output_html}")


# ---------- MAIN WORKFLOW ----------
def main():
    global driver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.maximize_window()

    # Load or resume from CSV
    if os.path.exists(WORKING_CSV):
        print(f"🔁 Resuming from {WORKING_CSV}")
        df = pd.read_csv(WORKING_CSV)
    else:
        print(f"📥 Starting from base CSV: {INPUT_CSV}")
        df = pd.read_csv(INPUT_CSV)
        for col in ["Latitude", "Longitude", "Host Duration", "Host Image Path", "Lens Link", "Google Maps Link"]:
            if col not in df.columns:
                df[col] = ""

    # Determine unprocessed rows
    to_process = df[df["Latitude"].isna() | (df["Latitude"] == "")]
    total_pending = len(to_process)
    print(f"🧮 {total_pending} listings need processing.\n")

    processed_since_save = 0

    for i, (idx, row) in enumerate(to_process.iterrows(), 1):
        if stop_requested:
            break

        listing_url = safe_str(row["URL"])
        listing_id = safe_str(row["Listing ID"])
        image_url = safe_str(row["Image URL"])

        print(f"➡️  [{i}/{total_pending}] Processing {listing_id}")

        try:
            data = get_listing_data(listing_url, listing_id)

            df.at[idx, "Latitude"] = safe_str(data["lat"])
            df.at[idx, "Longitude"] = safe_str(data["lng"])
            df.at[idx, "Host Duration"] = safe_str(data["host_duration"])
            df.at[idx, "Host Image Path"] = safe_str(data["host_image_path"])

            # Add Lens link
            if image_url.startswith("http"):
                df.at[idx, "Lens Link"] = (
                    f"https://lens.google.com/uploadbyurl?url={image_url}&hl=en&gl=id&q=what+is+the+address+and+map+location+of+this"
                )

            # Add Google Maps link if lat/lng found
            if data["lat"] and data["lng"]:
                df.at[idx, "Google Maps Link"] = f"https://www.google.com/maps?q={data['lat']},{data['lng']}"
            else:
                df.at[idx, "Google Maps Link"] = ""

            processed_since_save += 1
            if processed_since_save >= SAVE_INTERVAL:
                df.to_csv(WORKING_CSV, index=False)
                print(f"💾 Progress saved to {WORKING_CSV}")
                processed_since_save = 0

        except Exception as e:
            print(f"⚠️ Error processing {listing_id}: {e}")
            continue

    # Save and close browser
    df.to_csv(WORKING_CSV, index=False)
    print("💾 CSV augmentation completed and saved.")
    driver.quit()
    print("✅ Chrome closed cleanly.")

    # Generate HTML at the end
    generate_html_from_csv(WORKING_CSV, FINAL_HTML)


if __name__ == "__main__":
    main()
