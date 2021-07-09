# TODO consolidate more code into functions
# TODO check latest entry in DB and add last_tweet to log and DB if not present
# TODO sentiment analysis

## Modules ##
from pytwitterscraper import TwitterScraper # Twitter scraper no API required
import webbrowser                           # Web browser
import time                                 # Wait
import re                                   # Regex
import winsound                             # Play Windows sounds
import sys                                  # Write to files
import argparse                             # Change elon to someone else if desired
import datetime                             # Timestamp
from new_row import new_row                 # Add new rows to database

## Variables ##

# Save original standard output for logging
original_stdout = sys.stdout

# Argument parser
parser = argparse.ArgumentParser(argument_default=argparse.SUPPRESS)
parser.add_argument("username", nargs="?", default="elonmusk")
args = parser.parse_args()

# Get Twitter handle from argument or default to Elon Musk
twitter_handle = args.username

# Create twitter scraper object
tw = TwitterScraper()

# Get Twitter profile data
profile = tw.get_profile(name=twitter_handle).__dict__
profile_photo = profile["profileurl"]
profile_banner = profile["bannerurl"]

# Get Twitter ID
twitter_id = profile["id"]

# Get last 2 tweets and compare IDs to filter pinned tweets
last_tweet_contents = tw.get_tweets(twitter_id, count=2).contents
last_tweet_id = last_tweet_contents[0]["id"]
last_tweet_id_2 = last_tweet_contents[1]["id"]
if last_tweet_id_2 > last_tweet_id:
    last_tweet_id = last_tweet_id_2

# Store empty new tweet ID and text strings to avoid errors
new_tweet_id = ""
new_tweet_text = ""

# Keywords
keywords = "Crypto|crypto|BTC|btc|Bitcoin|bitcoin|DOGE|Doge|doge|💦|🚀|🌙|🌕|🌜|🌛|CUM|Cum|cum|Rocket|rocket|Shib|shib|Moon|moon|Money|money|Economy|economy|Market|market"

# Regular expression for uppercase characters
regex_uppercase_pattern = ['[A-Z]+']

# Timestamp
timestamp = format(datetime.datetime.now())

# Iterator
i = 1

## Functions ##

# Convert a list to a string  
def listToString(s):     
    str1 = ""      
    for ele in s: 
        str1 += ele      
    return str1

# Remove characters that break INSERT  
def format_regex(r):
    r.replace("\'", "").replace(" ", "").replace("[", "").replace("]", "").replace(",", "")
    return r

# Make tweet URL
def make_url():
    url = "https://twitter.com/" + twitter_handle + "/status/" + format(new_tweet_id)
    return url

## Scrape Twitter and open in browser if new tweet, profile photo changed, or banner changed ##
while True:
    try:
        # Get new profile data
        new_profile = tw.get_profile(name=twitter_handle).__dict__
        new_profile_photo = new_profile["profileurl"]
        new_profile_banner = new_profile["bannerurl"]
    except:
        print("Bad profile \n")
    try:
        # Get 2 latest tweets and compare to filter a pinned
        new_tweet_contents = tw.get_tweets(twitter_id, count=2).contents
        new_tweet_id = new_tweet_contents[1]["id"]
        new_tweet_id_2 = new_tweet_contents[0]["id"]
        if new_tweet_id_2 > new_tweet_id:
            newest_tweet = 0
            new_tweet_id = new_tweet_id_2
        else:
            newest_tweet = 1
        new_tweet_text = new_tweet_contents[newest_tweet]["text"]
        # Compare new tweet to last tweet
        if new_tweet_id != last_tweet_id and new_tweet_id > last_tweet_id:
            webbrowser.open(make_url(), new=1)
        # Compare profile URL
        if new_profile_photo != profile_photo:
            webbrowser.open(new_profile_photo, new=1) 
        # Compare banner URL
        if new_profile_banner != profile_banner:
            webbrowser.open(new_profile_banner, new=1)
    except:
        print("Bad tweet \n")

    ## Print results to console ##
    print("Iteration:", i)
    print("Timestamp:", timestamp)
    print("Twitter Handle: @" + twitter_handle)
    # Tweets
    print("Tweet ID:", new_tweet_id)
    print("Tweet Text:", new_tweet_text)       
    try:
        # Regular expression for keywords
        regex = re.search(keywords, new_tweet_text)
        try:
            print("Keywords:", regex[0])
            regex = regex[0]
        except:
            print("Keywords:", regex)
        for p in regex_uppercase_pattern:
            regex_uppercase = format_regex(listToString(re.findall(p, new_tweet_text)))
        print("Upper Case:", regex_uppercase)
    except:
        print("Regex error")
    print("Tweet URL:", make_url(), "\n")

    ## Print results to log if new tweet, profile URL changed, or banner changed ##
    try:
        # Tweets
        if new_tweet_id > last_tweet_id:
            with open("twitter.log", "a", encoding="utf-8") as log:
                sys.stdout = log 
                print("Timestamp:", timestamp)
                print("Twitter Handle: @" + twitter_handle)
                print("Tweet ID:", new_tweet_id)
                print("Tweet Text:", new_tweet_text)
                print("Keywords:", regex)
                print("Upper Case:", regex_uppercase)
                print("Tweet URL:", make_url(), "\n")
                # Reset the standard output
                sys.stdout = original_stdout 
        # Photo
        if new_profile_photo != profile_photo:
            with open("twitter.log", "a") as log:
                sys.stdout = log 
                print("Timestamp:", timestamp)
                print("Twitter Handle: @" + twitter_handle)
                print("Profile URL:", new_profile_photo, "\n")
                # Reset the standard output
                sys.stdout = original_stdout
        # Banner
        if new_profile_banner != profile_banner:
            with open("twitter.log", "a") as log:
                sys.stdout = log 
                print("Timestamp:", timestamp)
                print("Twitter Handle: @" + twitter_handle)
                print("Banner URL:", new_profile_banner, "\n")
                # Reset the standard output
                sys.stdout = original_stdout
    except:
        print("Log error \n")

    ## Update twitter table in database ##
    if new_tweet_id > last_tweet_id or new_profile_photo != profile_photo or new_profile_banner != profile_banner:
        new_row()        
    
    ## Play sound if keyword found or image changed ##
    try:
        if re.search(keywords, new_tweet_text) and new_tweet_id > last_tweet_id or new_profile_photo != profile_photo or new_profile_banner != profile_banner:
            winsound.PlaySound("sound2.wav", winsound.SND_ASYNC)
    except:
        pass
        
    # Feeling brave? Add exchange API code here
    # if re.search("DOGE|Doge|doge",new_tweet_text) and new_tweet_id > last_tweet_id:
    # if re.search("BTC|DOGE|btc|Bitcoin|bitcoin",new_tweet_text) and new_tweet_id > last_tweet_id:

    ## Update tweet ID, profile URL, and banner URL ##
    if new_tweet_id > last_tweet_id:
        last_tweet_id = new_tweet_id
    if new_profile_photo != profile_photo:
        profile_photo = new_profile_photo
    if new_profile_banner != profile_banner:
        profile_banner = new_profile_banner

    ##  Update iterator ##
    i += 1
        
    ## Wait 5 seconds ##
    time.sleep(5) 