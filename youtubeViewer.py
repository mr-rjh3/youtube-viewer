# Imports
from datetime import datetime
import json
import re
import requests
from bs4 import BeautifulSoup
from hashlib import blake2b
from alive_progress import alive_bar

def scrapeTrendingPage(URL, verbose=False):

    # try to get the page / URL to scrape
    try:
        page = requests.get(URL)
    except:
        # print("Error: Could not scrape URL: ", URL)
        return
    
    # Initialize the BeautifulSoup object using the page text
    soup = BeautifulSoup(bytes(page.text, encoding="utf-8"), "html.parser")

    # Extract the links from the page
    script = soup.find("script", string=re.compile('var ytInitialData'))

    # Extract the JSON part from the script content
    script_content = script.string
    start_index = script_content.find('{')
    end_index = script_content.rfind('}') + 1
    json_str = script_content[start_index:end_index]
    
    yt_data = json.loads(json_str)

    # For debugging, dumps javascript variables of page to json for easier viewing
    # with open("yt_data/" + H + ".json", "w", encoding="utf-8") as f:
    #     json.dump(yt_data, f, indent=4)

    trending_urls = []

    if 'contents' in yt_data and 'twoColumnBrowseResultsRenderer' in yt_data['contents']:
        contents = yt_data['contents']['twoColumnBrowseResultsRenderer']['tabs'][0]['tabRenderer']['content']
        
        for section in contents['sectionListRenderer']['contents']:
            if 'itemSectionRenderer' in section:
                for item in section['itemSectionRenderer']['contents']:
                    if 'shelfRenderer' in item:
                        try:
                            for video_item in item['shelfRenderer']['content']['expandedShelfContentsRenderer']['items']:
                                    if 'videoRenderer' in video_item:
                                        video_id = video_item['videoRenderer']['videoId']
                                        watch_url = f"https://www.youtube.com/watch?v={video_id}"
                                        trending_urls.append(watch_url)
                        except KeyError as e:
                            if(verbose): print("Could not find key with error: ", e, "... skipping iteration of loop")
                            continue
                            
    return trending_urls

def scrapeVideo(URL, maxdepth, videos_watched, rewrite, doSuggestedVideos, bar, verbose=False, depth=0):
    if(depth == maxdepth):
        # We have reached the maximum depth so we will return
        # print("Maximum depth reached")
        return
    
    # Find the hash of the URL
    H = blake2b(bytes(URL, encoding='utf-8')).hexdigest()
    
    # try to get the page / URL to scrape
    try:
        page = requests.get(URL)
    except:
        # print("Error: Could not scrape URL: ", URL)
        return
    
    # Write to the log file
    if(verbose):
        print(f"<{URL}, {depth}, {maxdepth}>")
    with open("crawler1.log", "a") as f:
        # <H,URL,Download DateTime, HTTP Response Code>
        f.write("<" + H + ", " + URL + ", " + datetime.now().strftime("%d/%m/%Y %H:%M:%S") + ", " + str(page.status_code) + ">\n")

    # Initialize the BeautifulSoup object using the page text
    soup = BeautifulSoup(bytes(page.text, encoding="utf-8"), "html.parser")

    # Extract the links from the page
    script = soup.find("script", string=re.compile('var ytInitialData'))

    # Extract the JSON part from the script content
    script_content = script.string
    start_index = script_content.find('{')
    end_index = script_content.rfind('}') + 1
    json_str = script_content[start_index:end_index]
    
    yt_data = json.loads(json_str)

    # For debugging, dumps javascript variables of page to json for easier viewing
    # with open(f"yt_data/{depth}-" + H + ".json", "w", encoding="utf-8") as f:
    #     json.dump(yt_data, f, indent=4)

    video_data = {}
    video_data["depth"] = depth

    # -------------video title-------------
    try:
        video_data["title"] = yt_data['contents']['twoColumnWatchNextResults']['results']['results']['contents'][0]['videoPrimaryInfoRenderer']['title']['runs'][0]['text']
    except KeyError as e:
        if(verbose): print("Could not find key:", e, "... inputing N/A")
        video_data["title"] = "N/A"
    # -------------video channel-------------
    try:
        video_data["channel"] = yt_data['contents']['twoColumnWatchNextResults']['results']['results']['contents'][1]['videoSecondaryInfoRenderer']['owner']['videoOwnerRenderer']['title']['runs'][0]['text']
    except KeyError as e:
        if(verbose): print("Could not find key:", e, "... inputing N/A")
        video_data["channel"] = "N/A"
    try:
        video_data["channel_tag"] = yt_data['contents']['twoColumnWatchNextResults']['results']['results']['contents'][1]['videoSecondaryInfoRenderer']['owner']['videoOwnerRenderer']['title']['runs'][0]['navigationEndpoint']['commandMetadata']['webCommandMetadata']['url']
    except KeyError as e:
        if(verbose): print("Could not find key:", e, "..., inputing N/A")
        video_data["channel_tag"] = "N/A"
    # -------------upload date-------------
    try:
        video_data["upload_date"] = yt_data['contents']['twoColumnWatchNextResults']['results']['results']['contents'][0]['videoPrimaryInfoRenderer']['dateText']['simpleText']
    except KeyError as e:
        if(verbose): print("Could not find key:", e, "..., inputing N/A")
        video_data["upload_date"] = "N/A"
    # -------------views-------------
    try:
        video_data["view_count"] = yt_data['contents']['twoColumnWatchNextResults']['results']['results']['contents'][0]['videoPrimaryInfoRenderer']['viewCount']['videoViewCountRenderer']['viewCount']['simpleText']
    except KeyError as e:
        if(verbose): print("Could not find key:", e, "..., inputing N/A")
        video_data["view_count"] = "N/A"
    # -------------description-------------
    try:
        video_data["description"] = yt_data['contents']['twoColumnWatchNextResults']['results']['results']['contents'][1]['videoSecondaryInfoRenderer']['attributedDescription']['content']
    except KeyError as e:
        if(verbose): print("Could not find key:", e, "... inputing N/A")
        video_data["description"] = "N/A"
    # -------------Likes-------------
    try:
        video_data["likes"] = yt_data['contents']['twoColumnWatchNextResults']['results']['results']['contents'][0]['videoPrimaryInfoRenderer']['videoActions']['menuRenderer']['topLevelButtons'][0]['segmentedLikeDislikeButtonViewModel']['likeCountEntity']['likeCountIfIndifferentNumber']
    except KeyError as e:
        if(verbose): print("Could not find Likes key:", e, "... trying simplified like number")
        try:
            video_data["likes"] = yt_data['contents']['twoColumnWatchNextResults']['results']['results']['contents'][0]['videoPrimaryInfoRenderer']['videoActions']['menuRenderer']['topLevelButtons'][0]['segmentedLikeDislikeButtonViewModel']['likeButtonViewModel']['likeButtonViewModel']['toggleButtonViewModel']['toggleButtonViewModel']['defaultButtonViewModel']['buttonViewModel']['title']
        except KeyError as e:
            if(verbose): print("Could not find Likes key:", e, "... entering N/A.")
            video_data["likes"] = "N/A"
    # -------------CURRENT URL-------------
    video_data["URL"] = URL
    # -------------NEXT URL-------------
    # TODO: make sure the next video is not a short
    if(doSuggestedVideos): # if doSuggestedVideos is true, get suggested video URL first
        try:
            next_video_id = yt_data['contents']['twoColumnWatchNextResults']['secondaryResults']['secondaryResults']['results'][0]['compactVideoRenderer']['navigationEndpoint']['commandMetadata']['webCommandMetadata']['url']
        except KeyError as e:
            # if suggested video fails try suggested
            if(verbose): print("Could not find suggested video key:", e, "..., trying autoplay video")
            try:
                next_video_id = yt_data['contents']['twoColumnWatchNextResults']['autoplay']['autoplay']['sets'][0]['autoplayVideo']['commandMetadata']['webCommandMetadata']['url']
            except KeyError as e:
                # if both fail return
                print("KEY ERROR: ", e)
                with open(f"yt_data/depth-{depth}-KEYERROR-{e}-" + H + ".json", "w", encoding="utf-8") as f:
                    json.dump(yt_data, f, indent=4)
                print("Could not find the next video..., returning at depth: ", depth)
                return
    else: # Otherwise get next autoplay video
        try:
            next_video_id = yt_data['contents']['twoColumnWatchNextResults']['autoplay']['autoplay']['sets'][0]['autoplayVideo']['commandMetadata']['webCommandMetadata']['url']
        except KeyError as e:
            # if autoplay video fails try suggested
            if(verbose): print("Could not find autoplay video key:", e, "..., trying first suggested video")
            try:
                next_video_id = yt_data['contents']['twoColumnWatchNextResults']['secondaryResults']['secondaryResults']['results']['compactVideoRenderer'][0]['navigationEndpoint']['commandMetadata']['webCommandMetadata']['url']
            except KeyError as e:
                # if both fail return
                print("KEY ERROR: ", e)
                with open(f"yt_data/depth-{depth}-KEYERROR-{e}-" + H + ".json", "w", encoding="utf-8") as f:
                    json.dump(yt_data, f, indent=4)
                print("Could not find the next video..., returning at depth: ", depth)
                return
    next_watch_url = f"https://www.youtube.com{next_video_id}"
    
    # check if we have seen this video before
    try:
        videos_watched[H]["seen_count"] += 1
    except KeyError:
        videos_watched[H] = video_data
        videos_watched[H]["seen_count"] = 1

    bar()
    scrapeVideo(next_watch_url, maxdepth, videos_watched, rewrite, doSuggestedVideos, bar, verbose, depth+1)  
