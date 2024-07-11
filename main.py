import os
import re
import testAPI
import json
from pyyoutube import Api
from alive_progress import alive_bar
import argparse;

# TODO: look at youtube's api:  https://developers.google.com/youtube/v3/docs
# specifically: VideoCategories, Videos, search, list, and other things that may be useful!

def dumpDictToJSON(dict, directory):
    with open(f"{directory}.json", "w", encoding="utf-8") as f:
        json.dump(dict, f, indent=4)

if __name__ == "__main__":

    print("Welcome to the youtube viewer! ")
    print()
    print("How many root videos would you like? (int 1-100)")
    while True:
        rootVideos = (int)(input("Enter your choice: "))
        if(rootVideos < 1 or rootVideos > 100):
            print("Please enter an integer between 1 and 100")
        else:
            break
    print("What would you like the max depth to be? (int 1-1000)")
    while True:
        maxDepth = (int)(input("Enter your choice: "))
        if(maxDepth < 1 or maxDepth > 1000):
            print("Please enter an integer between 1 and 1000")
        else:
            break
    print("What would you like the max depth to be? (int 1-1000)")
    while True:
        maxDepth = (int)(input("Enter your choice: "))
        if(maxDepth < 1 or maxDepth > 1000):
            print("Please enter an integer between 1 and 1000")
        else:
            break
    
    print(f"Running youtubeViewer with {rootVideos} roots with a max depth of {maxDepth}...")

    api = Api(api_key="REPLACE_WITH_YOUR_OWN_API_KEY")
    videos_by_chart = api.get_videos_by_chart(chart="mostPopular", region_code="US", count=rootVideos)
    videoNum = 0
    for video in videos_by_chart.items:
        videoNum += 1
        directory = f"api_data/{video.id}"
        if(os.path.exists(directory)):
            print(f"Directory exists for video: {video.id}. Skipping to next video!")
            continue
        os.mkdir(directory)
        with alive_bar(maxDepth, title=f"Video: {videoNum} - Root-ID: {video.id}", enrich_print=True) as bar:
            watchedVideos, deadends = testAPI.getVideos(maxDepth, video.id, api, bar)

        dumpDictToJSON(watchedVideos, f"{directory}/Videos")
        dumpDictToJSON(deadends, f"{directory}/Deadends")