# Imports
import argparse
from datetime import datetime
import json
import os.path
import re
import time
import requests
from bs4 import BeautifulSoup
from hashlib import blake2b

def scrapeTrendingPage(URL, rewrite):
    # Find the hash of the URL
    H = blake2b(bytes(URL, encoding='utf-8')).hexdigest()

    # check if H.txt exists (H is the hash of the URL)
    if(os.path.isfile("pages/" + H + ".txt") and not rewrite):
        # File exists, however we do not want to rewrite it so we will return
        # print("File already exists")
        return

    # either the file does not exist or we want to rewrite it so we will continue to scraping the URL
    
    # try to get the page / URL to scrape
    try:
        page = requests.get(URL)
    except:
        # print("Error: Could not scrape URL: ", URL)
        return
    
    # Create / rewrite the file
    with open("pages/"+ H + ".txt", "w", encoding="utf-8") as f:
        f.write(page.text)

    # Initialize the BeautifulSoup object from the file we just created
    with open("pages/" + H + ".txt", "r", encoding="utf-8") as f:
        soup = BeautifulSoup(bytes(f.read(), encoding="utf-8"), "html.parser")

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
                            print("Could not find key with error: ", e, "... skipping iteration of loop")
                            continue
                            
    return trending_urls

def scrapeVideo(URL, maxdepth, videos_watched, rewrite, verbose=False, depth=0):
    if(depth == maxdepth):
        # We have reached the maximum depth so we will return
        # print("Maximum depth reached")
        return
    # Find the hash of the URL
    H = blake2b(bytes(URL, encoding='utf-8')).hexdigest()

    # check if H.txt exists (H is the hash of the URL)
    if(os.path.isfile("pages/" + H + ".txt") and not rewrite):
        # File exists, however we do not want to rewrite it so we will return
        # print("File already exists")
        return

    # either the file does not exist or we want to rewrite it so we will continue to scraping the URL
    
    # try to get the page / URL to scrape
    try:
        page = requests.get(URL)
    except:
        # print("Error: Could not scrape URL: ", URL)
        return
    
    # Write to the log file
    if(verbose):
        print("<" + URL + ",", depth, ">")
    with open("crawler1.log", "a") as f:
        # <H,URL,Download DateTime, HTTP Response Code>
        f.write("<" + H + ", " + URL + ", " + datetime.now().strftime("%d/%m/%Y %H:%M:%S") + ", " + str(page.status_code) + ">\n")

    # print("Scraping URL: ", URL)
    # Create / rewrite the file
    with open("pages/"+ H + ".txt", "w", encoding="utf-8") as f:
        f.write(page.text)

    # Initialize the BeautifulSoup object from the file we just created
    with open("pages/" + H + ".txt", "r", encoding="utf-8") as f:
        soup = BeautifulSoup(bytes(f.read(), encoding="utf-8"), "html.parser")

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

    video_data = {}

    if 'contents' in yt_data and 'twoColumnWatchNextResults' in yt_data['contents']:
        
        # video title
        try:
            video_data["title"] = yt_data['contents']['twoColumnWatchNextResults']['results']['results']['contents'][0]['videoPrimaryInfoRenderer']['title']['runs'][0]['text']
        except KeyError as e:
            print("Could not find key:", e, "... inputing N/A")
            video_data["title"] = "N/A"
        # video channel
        try:
            video_data["channel"] = yt_data['contents']['twoColumnWatchNextResults']['results']['results']['contents'][1]['videoSecondaryInfoRenderer']['owner']['videoOwnerRenderer']['title']['runs'][0]['text']
        except KeyError as e:
            print("Could not find key:", e, "... inputing N/A")
            video_data["channel"] = "N/A"
        try:
            video_data["channel_tag"] = yt_data['contents']['twoColumnWatchNextResults']['results']['results']['contents'][1]['videoSecondaryInfoRenderer']['owner']['videoOwnerRenderer']['title']['runs'][0]['navigationEndpoint']['commandMetadata']['webCommandMetadata']['url']
        except KeyError as e:
            print("Could not find key:", e, "..., inputing N/A")
            video_data["channel_tag"] = "N/A"
        
        # upload date
        try:
            video_data["upload_date"] = yt_data['contents']['twoColumnWatchNextResults']['results']['results']['contents'][0]['videoPrimaryInfoRenderer']['dateText']['simpleText']
        except KeyError as e:
            print("Could not find key:", e, "..., inputing N/A")
            video_data["upload_date"] = "N/A"
        # views
        try:
            video_data["view_count"] = yt_data['contents']['twoColumnWatchNextResults']['results']['results']['contents'][0]['videoPrimaryInfoRenderer']['viewCount']['videoViewCountRenderer']['originalViewCount']
        except KeyError as e:
            print("Could not find key:", e, "..., inputing N/A")
            video_data["view_count"] = "N/A"
        # description
        try:
            video_data["description"] = yt_data['contents']['twoColumnWatchNextResults']['results']['results']['contents'][1]['videoSecondaryInfoRenderer']['attributedDescription']['content']
        except KeyError as e:
            print("Could not find key:", e, "... inputing N/A")
            video_data["description"] = "N/A"
        # description
        try:
            video_data["likes"] = yt_data['contents']['twoColumnWatchNextResults']['results']['results']['contents'][0]['videoPrimaryInfoRenderer']['videoActions']['menuRenderer']['topLevelButtons'][0]['segmentedLikeDislikeButtonViewModel']['likeCountEntity']['likeCountIfIndifferentNumber']
        except KeyError as e:
            print("Could not find key:", e, "... inputing N/A")
            video_data["likes"] = "N/A"
        # URL
        try:
            next_video_id = yt_data['contents']['twoColumnWatchNextResults']['autoplay']['autoplay']['sets'][0]['autoplayVideo']['commandMetadata']['webCommandMetadata']['url']
        except KeyError as e:
            print("Could not find key:", e, "...URL, trying first suggested video")
            try:
                next_video_id = yt_data['contents']['twoColumnWatchNextResults']['autoplay']['autoplay']['sets'][0]['autoplayVideo']['commandMetadata']['webCommandMetadata']['url']
            except KeyError as e:
                print("Could not find key:", e, "...video, returning at depth: ", depth)
                return
        next_watch_url = f"https://www.youtube.com{next_video_id}"
        video_data["URL"] = next_watch_url

    videos_watched[H] = video_data
    scrapeVideo(next_watch_url, maxdepth, videos_watched, rewrite, verbose, depth+1)  


def int_range(mini,maxi):
    """Return function handle of an argument type function for 
       ArgumentParser checking a int range: mini <= arg <= maxi
         mini - minimum acceptable argument
         maxi - maximum acceptable argument"""

    # Define the function with default arguments
    def float_range_checker(arg):
        """New Type function for argparse - a float within predefined range."""
        try:
            i = int(arg)
        except ValueError:    
            raise argparse.ArgumentTypeError("Must be a integer")
        if i < mini or i > maxi:
            raise argparse.ArgumentTypeError("Must be in range [" + str(mini) + " .. " + str(maxi)+"]")
        return i
    # Return function handle to checking function
    return float_range_checker

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Web scraper for a Google Scholar page.')
    parser.add_argument("-d", "--maxDepth", help="Maximum depth of videos to crawl.", default=3, type=int_range(1,1000))
    parser.add_argument("-t", "--maxRoots", help="Maximum number of root URLs from the trending page that will be crawled from.", default=3, type=int_range(1,100))
    parser.add_argument("-r", "--rewrite", help="If True while the file H.txt exists for the current URL re-download and re-write the file. Default value is False.", action="store_true", default=False)
    parser.add_argument("-v", "--verbose", help="if True, print <URL,depth> on the screen. Default value is False.", action="store_true", default=False)
    args = parser.parse_args()

    trending_URLS = scrapeTrendingPage("https://www.youtube.com/feed/trending", args.rewrite)
    if(len(trending_URLS) < args.maxRoots):
        print(f"There are only {len(trending_URLS)} trending videos. Running with all trending videos instead")
        args.maxRoots = len(trending_URLS)
    print(f"Scraping the first {args.maxRoots} trending videos, with a max depth of:", args.maxDepth)
    
    print(len(trending_URLS))
    for i in range(args.maxRoots):
        print(f"Trending video {i+1}...")
        watched_dict = {}
        scrapeVideo(trending_URLS[i], args.maxDepth, watched_dict, args.rewrite, verbose=args.verbose)
        with open(f"yt_data/root_{i}-videos_watched.json", "w", encoding="utf-8") as f:
            json.dump(watched_dict, f, indent=4)
    