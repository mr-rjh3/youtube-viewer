from datetime import datetime
import json
import re
import requests
from bs4 import BeautifulSoup



"""
----------------------------------------------------------
Populates dictionary with a chain of youtube videos by continuously getting the first suggested video for each video 
Use: watchedDict = getVideos(maxDepth=10, rootID="suO6X5U4rmQ")
----------------------------------------------------------
Parameters:
    maxDepth - maximum depth the function will run to
    rootID - The initial video to start the chain on
    api - the youtube api to fetch video data
    bar - alive_progress progress bar
Returns:
    watchedDict - All the youtube videos seen, indexed with thier youtube ID
----------------------------------------------------------
"""
def getVideos(maxDepth, rootID, api, bar):
    depth = 0 # initialize depth to 0
    IDs = [rootID] # Initialze ID stack 
    watchedDict = {}
    deadends = {} # Initialize a dictionary of dead end IDs to avoid

    while(depth < maxDepth):
        # add the video data to the dictionary
        # print(currID)

        # check if we have visited this id before and update seen count and depth list
        try:
            watchedDict[IDs[-1]]["seenCount"] += 1
            watchedDict[IDs[-1]]['depths'].append(depth)
        except KeyError:
            try:
                watchedDict[IDs[-1]] = api.get_video_by_id(video_id=IDs[-1]).to_dict()
            except:
                print(IDs[-2], IDs[-1])
                with open(f"errors/{IDs[-2]}.json", "w", encoding="utf-8") as f:
                    json.dump(yt_data, f, indent=4)
                exit(-1)
            watchedDict[IDs[-1]]["seenCount"] = 1
            watchedDict[IDs[-1]]['depths'] = [depth]


        # try to get the page / URL to scrape
        URL = f"https://youtube.com/watch?v={IDs[-1]}" # set URL to current ID
        try:
            page = requests.get(URL)
        except:
            # print("Error: Could not scrape URL: ", URL)
            return -1
        # Write the page to the log file
        with open("crawler1.log", "a") as f:
            # <ID,URL,Download DateTime, HTTP Response Code>
            f.write("<" + IDs[-1] + ", " + URL + ", " + datetime.now().strftime("%d/%m/%Y %H:%M:%S") + ", " + str(page.status_code) + ">\n")
        
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
        # keep getting suggested video until
        newID = getSuggestedVideo(yt_data, deadends)
        if(newID == -1):
            # could not find new ID, label this ID as a dead end 
            print(f"{IDs[-1]} is deadend! Returning to previous ID.")
            deadends[IDs[-1]] = IDs[-1]
            IDs.pop()
        else:
            IDs.append(newID)
            depth += 1
            bar() # update progress bar
    
    return watchedDict, deadends

"""
----------------------------------------------------------
Finds the first suggested video ID from the given json dictionary
Use: ID = getSuggestedVideo(yt_data)
----------------------------------------------------------
Parameters:
    yt_data - Dictionary of the javascript variables stored in the youtube page, this should have a suggested video and can come in different forms.
    deadends - Dictionary of IDs that do not lead to new videos, avoid these IDs.
Returns:
    ID - ID of the first suggested video
----------------------------------------------------------
"""
def getSuggestedVideo(yt_data, deadends):
    # find the next suggested video from a given youtube page
    try:
        ID = yt_data["responseContext"]["webResponseContextExtensionData"]["webPrefetchData"]["navigationEndpoints"][0]["watchEndpoint"]["videoId"]
        return ID 
    except KeyError:
        ""

    # Try compactVideoRenderer
    try:
        for result in yt_data["contents"]["twoColumnWatchNextResults"]["secondaryResults"]["secondaryResults"]["results"]:
            ID = result["compactVideoRenderer"]["videoId"]
            try:
                # if ID is in deadends, continue the loop
                deadends[ID]
                continue
            except KeyError:
                # If ID is not in deadends return it.
                return ID
    except KeyError:
        ""

    # Try richGridRenderer
    try:
        for item in yt_data["contents"]["twoColumnWatchNextResults"]["secondaryResults"]["secondaryResults"]["results"][0]["richGridRenderer"]["contents"]:
            ID = item["richItemRenderer"]["content"]["videoRenderer"]["videoId"]
            try:
                # if ID is in deadends, continue the loop
                deadends[ID]
                continue
            except KeyError:
                # If ID is not in deadends return it.
                return ID
    except KeyError:
        ""
    return -1


