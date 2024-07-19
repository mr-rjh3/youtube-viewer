# using json files plot findings using plotly
# Most popular channels, bar graph of channels sorted by number of videos
# Box plot for view count of each root path
# do some language processing and graph rate of words / phrases
# date range of uploads
# average likes for each root path
# average repeats for each root path

"""
The rapid and expansive growth of YouTube over the years has caused worry among creators and viewers alike that traction towards smaller channels 
has dwindled while large channels and businesses are pushed to the feed more often. I want to answer the following questions:

 - What defines a “large” channel vs. a “small” channel? 
    - views, subscribers, likes, comments
 - How often does YouTube recommend a small channel / video? 
    - define a range for large vs small
 - On average, what does YouTube usually recommend to users? 
    - Find the most common videos / categories throught all rootsf
 - Does YouTube have a bias towards larger creators and businesses? 
 - Does YouTube have a bias towards certain content categories? 

The purpose of this report is to analyze data gathered from YouTube and evaluate whether or not 
there is a bias within YouTube's recommendation algorithm and suggest methods to alleviate any biases.

What data do I have and what data is useful for answering these questions?

"""
import json
import os
# import plotly.express as px


rootVideos = os.listdir(f"api_data/maxDepth-1000")
totalVideos = 0

for rootID in rootVideos:
    try:
        with open(f"api_data/maxDepth-1000/{rootID}/videos.json", "r") as f:
            videoData = json.load(f)
        totalVideos += len(videoData)
    except FileNotFoundError:
        continue

print(f"Total videos from {len(rootVideos)} roots: {totalVideos}")