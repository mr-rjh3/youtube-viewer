import sys
import youtubeViewer
import argparse
import json
from alive_progress import alive_bar

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
    parser.add_argument("-s", "--suggestedVideos", help="Have the program focus on suggested videos instead of autoplay videos.", action="store_true", default=False)
    parser.add_argument("-r", "--rewrite", help="If True while the file H.txt exists for the current URL re-download and re-write the file. Default value is False.", action="store_true", default=False)
    parser.add_argument("-v", "--verbose", help="if True, print <URL,depth> on the screen as well as error messages. Default value is False.", action="store_true", default=False)
    args = parser.parse_args()

    trending_URLS = youtubeViewer.scrapeTrendingPage("https://www.youtube.com/feed/trending", args.rewrite)
    if(len(trending_URLS) < args.maxRoots):
        print(f"There are only {len(trending_URLS)} trending videos. Running with all trending videos instead")
        args.maxRoots = len(trending_URLS)
    print(f"Scraping the first {args.maxRoots} / {len(trending_URLS)} trending videos, with a max depth of:", args.maxDepth)

    if(args.suggestedVideos):
        print("Suggested videos set as priority!")
    else:
        print("Autoplay videos set as priority!")
    print("Current Recursion limit: ", sys.getrecursionlimit())
    sys.setrecursionlimit(10**6)
    print("New Recursion limit: ", sys.getrecursionlimit())
    for i in range(args.maxRoots):
        print(f"Trending video {i+1}...")
        watched_dict = {}
        with alive_bar(args.maxDepth, enrich_print=True) as bar:
            youtubeViewer.scrapeVideo(trending_URLS[i], args.maxDepth, watched_dict, args.rewrite, args.suggestedVideos, bar, verbose=args.verbose)
        
        with open(f"yt_data/root_{i+1}-videos_watched.json", "w", encoding="utf-8") as f:
            json.dump(watched_dict, f, indent=4)