import os
import re
import testAPI
import json
from pyyoutube import Api
from alive_progress import alive_bar
import argparse;

# TODO: look at youtube's api:  https://developers.google.com/youtube/v3/docs
# specifically: VideoCategories, Videos, search, list, and other things that may be useful!

class printColors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def dumpDictToJSON(dict, directory):
    with open(f"{directory}.json", "w", encoding="utf-8") as f:
        json.dump(dict, f, indent=4)

def int_range(mini,maxi):
    """Return function handle of an argument type function for 
       ArgumentParser checking a int range: mini <= arg <= maxi
         mini - minimum acceptable argument
         maxi - maximum acceptable argument"""

    # Define the function with default arguments
    def int_range_checker(arg):
        """New Type function for argparse - an int within predefined range."""
        try:
            i = int(arg)
        except ValueError:    
            raise argparse.ArgumentTypeError("Must be a integer")
        if i < mini or i > maxi:
            raise argparse.ArgumentTypeError("Must be in range [" + str(mini) + " .. " + str(maxi)+"]")
        return i
    # Return function handle to checking function
    return int_range_checker

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Iterates through youtube videos until maximum depth.')
    parser.add_argument("-r", "--rootVideos", help="Number of root videos to iterate through", type=int_range(1, 100), default=5)
    parser.add_argument("-d", "--maxDepth", help="Maximum depth for all root videos.", type=int_range(1, 1000), default=10)

    parser.add_argument("-re", "--rewrite", help="Tells the program to rewrite any already traversed root videos.", action="store_true")

    args = parser.parse_args()

    print(f"Running youtubeViewer with {printColors.BOLD}{args.rootVideos}{printColors.ENDC} roots and a max depth of {printColors.BOLD}{args.maxDepth}{printColors.ENDC}...")

    print(printColors.BOLD + "Rewrite mode: " + printColors.ENDC, printColors.GREEN + "On" if args.rewrite else printColors.RED + "Off", printColors.ENDC)

    api = Api(api_key="REPLACE_WITH_YOUR_OWN_API_KEY")
    videos_by_chart = api.get_videos_by_chart(chart="mostPopular", region_code="US", count=args.rootVideos)
    videoNum = 0

    for video in videos_by_chart.items:
        videoNum += 1
        path = f"api_data/maxDepth-{args.maxDepth}/{video.id}"
        if(os.path.exists(path)):
            if(not args.rewrite):
                print(f"{printColors.BOLD}Video: {videoNum} - Root-ID: {video.id}{printColors.ENDC} | {printColors.YELLOW}Directory already exists... Skipping to next video!{printColors.ENDC}")
                continue
        else:
            # If the path does not exist make it
            os.makedirs(path)
        
        with alive_bar(args.maxDepth, title=f"{printColors.BOLD}Video: {videoNum} - Root-ID: {video.id}{printColors.ENDC}", enrich_print=True) as bar:
            watchedVideos, deadends = testAPI.getVideos(args.maxDepth, video.id, api, bar)

        dumpDictToJSON(watchedVideos, f"{path}/Videos")
        dumpDictToJSON(deadends, f"{path}/Deadends")