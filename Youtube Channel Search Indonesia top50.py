# -*- coding: utf-8 -*-
"""
Created on Sun Sep  7 11:49:17 2025

@author: wb641752
"""
from googleapiclient.discovery import build
import os

API_KEY = 'AIzaSyDWJne7pObBJetiaYKHGnV9KJqL0iVfpV8'
REGION_CODE = 'ID'
MAX_RESULTS = 50
CHANNELS_FILE = 'IndonesiaTopYouTubechannels.txt'


# Initialize YouTube API
youtube = build('youtube', 'v3', developerKey=API_KEY)

# Load existing channel IDs from file
def load_existing_channels(filepath):
    if not os.path.exists(filepath):
        return set()
    with open(filepath, 'r', encoding='utf-8') as file:
        return set(line.strip().split(' ', 1)[0] for line in file if line.strip())

# Save a new channel to file
def save_new_channel(filepath, channel_id, channel_title):
    with open(filepath, 'a', encoding='utf-8') as file:
        file.write(f"{channel_id} {channel_title}\n")

# Get most popular videos in a region
def fetch_trending_channels():
    request = youtube.videos().list(
        part='snippet,statistics',
        chart='mostPopular',
        regionCode=REGION_CODE,
        maxResults=MAX_RESULTS
    )
    return request.execute()

# Main execution
def main():
    existing_channels = load_existing_channels(CHANNELS_FILE)
    print(f"Loaded {len(existing_channels)} existing channels.")

    response = fetch_trending_channels()
    new_count = 0

    for video in response['items']:
        snippet = video['snippet']
        statistics = video['statistics']
        
        channel_id = snippet['channelId']
        channel_title = snippet['channelTitle']
        
        if channel_id not in existing_channels:
            save_new_channel(CHANNELS_FILE, channel_id, channel_title)
            existing_channels.add(channel_id)
            new_count += 1
            print(f"Added: {channel_title} ({channel_id})")

    print(f"✅ Added {new_count} new channels.")
    print(f"📁 Total stored channels: {len(existing_channels)}")

if __name__ == '__main__':
    main()
