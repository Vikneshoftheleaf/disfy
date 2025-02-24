import os
import requests
from flask import Flask, render_template, request

app = Flask(__name__)

# Your YouTube API Key
YOUTUBE_API_KEY = 'AIzaSyAXq89ngRBgIhaQUA-LNJpZr6VhAFT4WP4'

# Define the YouTube API base URL
YOUTUBE_API_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_DETAILS_URL = "https://www.googleapis.com/youtube/v3/videos"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    query = request.form.get('query')
    if query:
        # Step 1: Make a request to the YouTube API to search for videos
        params = {
            'part': 'snippet',
            'q': query,
            'key': YOUTUBE_API_KEY,
            'maxResults': 50,
            'type': 'video',
        }
        response = requests.get(YOUTUBE_API_URL, params=params)

        if response.status_code == 200:
            search_results = response.json()

            video_ids = [item['id']['videoId'] for item in search_results['items']]

            # Step 2: Fetch video details (including duration)
            video_details_params = {
                'part': 'contentDetails',
                'id': ','.join(video_ids),
                'key': YOUTUBE_API_KEY
            }

            video_details_response = requests.get(YOUTUBE_VIDEO_DETAILS_URL, params=video_details_params)

            if video_details_response.status_code == 200:
                video_details = video_details_response.json()

                videos = []
                for item in search_results['items']:
                    video_id = item['id']['videoId']
                    video_duration = next((v['contentDetails']['duration'] for v in video_details['items'] if v['id'] == video_id), 'PT0S')
                    
                    # Convert ISO 8601 duration (e.g., PT1M30S -> 90 seconds)
                    duration_in_seconds = convert_duration_to_seconds(video_duration)

                    if duration_in_seconds > 60:
                        video = {
                            'title': item['snippet']['title'],
                            'description': item['snippet']['description'],
                            'thumbnail': item['snippet']['thumbnails']['high']['url'],
                            'url': f"https://www.youtube.com/watch?v={video_id}",
                            'video_id': video_id,
                            'video_thumb': f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg"
                        }
                        videos.append(video)

                return render_template('index.html', videos=videos)

            else:
                return "Error fetching video details from YouTube API"

        else:
            return "Error fetching results from YouTube API"

    return render_template('index.html')

def convert_duration_to_seconds(duration):
    
    import re

    pattern = re.compile(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?')
    matches = pattern.match(duration)
    
    hours = int(matches.group(1) or 0)
    minutes = int(matches.group(2) or 0)
    seconds = int(matches.group(3) or 0)

    return hours * 3600 + minutes * 60 + seconds

if __name__ == '__main__':
    app.run()
