from googleapiclient.discovery import build
import os

# ===============================
# CONFIGURATION
# ===============================
API_KEY = 'AIzaSyDWJne7pObBJetiaYKHGnV9KJqL0iVfpV8'  # <-- Replace with your valid YouTube API key
CHANNELS_FILE = 'IndonesiaTopYouTubechannels.txt'
MAX_RESULTS = 50

# Initialize YouTube API client
youtube = build('youtube', 'v3', developerKey=API_KEY)


# ===============================
# LOAD CHANNELS FROM FILE
# ===============================
def load_channels(filepath):
    """Load channel IDs and names from saved file."""
    if not os.path.exists(filepath):
        print("⚠️ No channel file found.")
        return []
    with open(filepath, 'r', encoding='utf-8') as file:
        channels = [line.strip().split(' ', 1) for line in file if line.strip()]
    return channels


# ===============================
# FETCH CHANNEL STATS
# ===============================
def get_channel_statistics(channel_id):
    """Return subscriber count, view count, video count, etc."""
    request = youtube.channels().list(
        part='snippet,statistics',
        id=channel_id
    )
    response = request.execute()

    if not response.get('items'):
        return None

    data = response['items'][0]
    snippet = data['snippet']
    stats = data['statistics']

    return {
        'channelId': channel_id,
        'title': snippet.get('title'),
        'description': snippet.get('description'),
        'publishedAt': snippet.get('publishedAt'),
        'subscribers': int(stats.get('subscriberCount', 0)),
        'totalViews': int(stats.get('viewCount', 0)),
        'totalVideos': int(stats.get('videoCount', 0))
    }


# ===============================
# FETCH VIDEOS FOR A CHANNEL
# ===============================
def get_channel_videos(channel_id, max_videos=None):
    """Fetch all (or top N) video IDs for a given channel."""
    videos = []
    next_page_token = None

    while True:
        request = youtube.search().list(
            part='id,snippet',
            channelId=channel_id,
            maxResults=MAX_RESULTS,
            order='date',  # latest first
            type='video',
            pageToken=next_page_token
        )
        response = request.execute()

        for item in response.get('items', []):
            video_id = item['id']['videoId']
            videos.append(video_id)

        next_page_token = response.get('nextPageToken')
        if not next_page_token or (max_videos and len(videos) >= max_videos):
            break

    return videos[:max_videos] if max_videos else videos


# ===============================
# FETCH VIDEO DETAILS
# ===============================
def get_video_details(video_ids):
    """Fetch view count, likes, comments, and description for each video."""
    all_details = []

    for i in range(0, len(video_ids), 50):  # API allows 50 at a time
        request = youtube.videos().list(
            part='snippet,statistics',
            id=','.join(video_ids[i:i + 50])
        )
        response = request.execute()

        for item in response.get('items', []):
            snippet = item['snippet']
            stats = item['statistics']
            video_id = item['id']

            details = {
                'videoId': video_id,
                'title': snippet.get('title'),
                'description': snippet.get('description'),
                'url': f"https://www.youtube.com/watch?v={video_id}",
                'views': int(stats.get('viewCount', 0)),
                'likes': int(stats.get('likeCount', 0)),
                'comments': int(stats.get('commentCount', 0))
            }
            all_details.append(details)

    return all_details


# ===============================
# MAIN EXECUTION LOGIC
# ===============================
def main():
    channels = load_channels(CHANNELS_FILE)
    if not channels:
        print("❌ No channels loaded.")
        return

    print(f"✅ Loaded {len(channels)} channels from file.\n")

    choice = input("Do you want to (1) fetch top N channels or (2) a specific channel ID? (1/2): ").strip()

    if choice == '1':
        n = int(input("Enter number of top channels to fetch: "))
        selected_channels = channels[:n]
    elif choice == '2':
        channel_id = input("Enter specific channel ID: ").strip()
        selected_channels = [[channel_id, "Custom Channel"]]
    else:
        print("Invalid choice.")
        return

    for channel_id, channel_name in selected_channels:
        print(f"\n📺 Fetching data for: {channel_name} ({channel_id}) ...")

        # 1️⃣ Channel statistics
        channel_stats = get_channel_statistics(channel_id)
        if not channel_stats:
            print("❌ Could not fetch channel details.")
            continue

        print(f"   Title: {channel_stats['title']}")
        print(f"   Description: {channel_stats['description']}")
        print(f"   Published At: {channel_stats['publishedAt']}")
        print(f"   Subscribers: {channel_stats['subscribers']:,}")
        print(f"   Total Views: {channel_stats['totalViews']:,}")
        print(f"   Total Videos: {channel_stats['totalVideos']:,}")



        # 2️⃣ Videos and their stats
        num_videos = int(input(f"Enter number of recent videos to fetch for {channel_name} (0 for all): "))
        video_ids = get_channel_videos(channel_id, None if num_videos == 0 else num_videos)
        video_details = get_video_details(video_ids)

        print(f"   🎥 Found {len(video_details)} videos.\n")

        for v in video_details:
            print(f"   ▶ {v['title']}")
            print(f"      URL: {v['url']}")
            print(f"      Views: {v['views']:,}, Likes: {v['likes']:,}, Comments: {v['comments']:,}")
            print(f"      Description: {v['description']}...\n")  

    print("\n✅ Data fetching complete.")


# ===============================
# ENTRY POINT
# ===============================
if __name__ == '__main__':
    main()
