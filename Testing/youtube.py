import random
import googleapiclient.discovery
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv('googleAPIkey')

def youtube_search(query, max_results=50):
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=API_KEY)
    request = youtube.search().list(
        q=query,
        part="snippet",
        type="video",
        maxResults=max_results
    )
    response = request.execute()
    return response

def get_random_video(videos):
    return random.choice(videos)

def main():
    query = "batata assada"
    response = youtube_search(query)
    videos = response.get("items", [])
    if not videos:
        print("No videos found.")
        return
    random_video = get_random_video(videos)
    video_id = random_video["id"]["videoId"]
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    video_description = random_video["snippet"]["description"]
    print("Video URL:", video_url)
    print("Description:", video_description)

if __name__ == "__main__":
    main()
